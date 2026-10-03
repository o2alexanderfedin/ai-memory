"""IngestPipeline orchestrator — wires adapter → idempotency → PII → chunker → fanout → persist."""
import asyncio
import json
import threading
from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

from ai_hive_memory.ingest.adapters.whatsapp import WhatsAppAdapter
from ai_hive_memory.ingest.chunker import Chunker
from ai_hive_memory.ingest.failure_policy import ExtractionFailurePolicy
from ai_hive_memory.ingest.idempotency import IdempotencyGuard
from ai_hive_memory.ingest.pipeline import IngestPipeline
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.ingest_repository import (
    ALL_DOMAINS,
    IngestJobRepository,
    PendingFactRepository,
)
from ai_hive_memory.storage.repository import PersonaRepository


def _bootstrap_persona(tenant_id: str) -> str:
    repo = PersonaRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        return repo.create_persona(conn, tenant_id)
    finally:
        gen.close()


def _mock_gateway() -> MagicMock:
    gw = MagicMock()
    gw.complete.return_value = json.dumps({})  # empty extraction (no facts) — schema valid
    return gw


def test_pipeline_processes_whatsapp_input_end_to_end() -> None:
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    raw = (
        b"[2026-04-21 12:00] Alice: Hi Bob!\n"
        b"[2026-04-21 12:01] Bob: Hello!\n"
    )
    pipeline = IngestPipeline(gateway=_mock_gateway())
    job_repo = IngestJobRepository()
    pf_repo = PendingFactRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        asyncio.run(pipeline.run(
            conn=conn, tenant_id=tenant_id, persona_id=persona_id,
            job_id=job_id, fmt="whatsapp", raw=raw,
        ))
        row = job_repo.get_job(conn, tenant_id, job_id)
        assert row is not None
        assert row["status"] == "DONE"
        # Empty payloads → 0 facts but job marks DONE
        assert pf_repo.list_for_job(conn, tenant_id, job_id) == []
    finally:
        gen.close()


def test_pipeline_persists_facts_when_extractor_returns_payload() -> None:
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    raw = b"[2026-04-21 12:00] Alice: I was born in Boston.\n"
    gw = MagicMock()
    # Biography returns a real payload; others empty.
    def _complete(*, tier: object, messages: list[dict[str, str]],
                  json_mode: bool, temperature: float = 0.0,
                  max_tokens: int = 2048) -> str:
        sys_msg = messages[0]["content"]
        if "biographical" in sys_msg.lower():
            return json.dumps({"birth_date_precision": "year"})
        return json.dumps({})
    gw.complete.side_effect = _complete
    pipeline = IngestPipeline(gateway=gw)
    job_repo = IngestJobRepository()
    pf_repo = PendingFactRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        asyncio.run(pipeline.run(
            conn=conn, tenant_id=tenant_id, persona_id=persona_id,
            job_id=job_id, fmt="whatsapp", raw=raw,
        ))
        facts = pf_repo.list_for_job(conn, tenant_id, job_id)
        assert any(f["domain"] == "biography" for f in facts)
    finally:
        gen.close()


class _FlakyGateway:
    """Fake LLM: domains whose prompt contains a key in `failures` raise that many times.

    A failure count of -1 means the domain always raises. Calls are counted per
    key so a test can tell a retried domain from one that was called once.
    """

    def __init__(self, failures: dict[str, int]) -> None:
        self._failures = failures
        self._lock = threading.Lock()
        self.calls: dict[str, int] = dict.fromkeys(failures, 0)

    def complete(self, *, tier: object, messages: list[dict[str, str]],
                 json_mode: bool, temperature: float = 0.0,
                 max_tokens: int = 2048) -> str:
        prompt = messages[0]["content"].lower()
        for key, times in self._failures.items():
            if key in prompt:
                with self._lock:
                    self.calls[key] += 1
                    n = self.calls[key]
                if times == -1 or n <= times:
                    raise TimeoutError(f"LLM timed out ({key}, call {n})")
        if "biographical" in prompt:
            return json.dumps({"birth_date_precision": "year"})
        return json.dumps({})


def _run_flaky(gw: _FlakyGateway) -> tuple[str, str, str]:
    """Run one whatsapp message through the pipeline; return (tenant, job, error-or-'')."""
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    pipeline = IngestPipeline(
        gateway=gw,  # type: ignore[arg-type]
        failure_policy=ExtractionFailurePolicy(base_delay_s=0.0),
    )
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = IngestJobRepository().create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        error = ""
        try:
            asyncio.run(pipeline.run(
                conn=conn, tenant_id=tenant_id, persona_id=persona_id, job_id=job_id,
                fmt="whatsapp", raw=b"[2026-04-21 12:00] Alice: I was born in 1990.\n",
            ))
        except Exception as e:
            error = str(e)
    finally:
        gen.close()
    return tenant_id, job_id, error


def _job(tenant_id: str, job_id: str) -> tuple[dict[str, Any], int]:  # type: ignore[explicit-any]
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        row = IngestJobRepository().get_job(conn, tenant_id, job_id)
        assert row is not None
        n_facts = len(PendingFactRepository().list_for_job(conn, tenant_id, job_id))
        return row, n_facts
    finally:
        gen.close()


def test_pipeline_retries_a_domain_whose_llm_call_fails_then_succeeds() -> None:
    max_attempts = ExtractionFailurePolicy().max_attempts
    gw = _FlakyGateway({"psychometric": max_attempts - 1})
    tenant_id, job_id, error = _run_flaky(gw)
    row, _ = _job(tenant_id, job_id)
    assert gw.calls["psychometric"] == max_attempts, (
        f"psychometrics extractor called {gw.calls['psychometric']} time(s); "
        "a failing LLM call must be retried up to max_attempts"
    )
    assert (error, row["status"]) == ("", "DONE"), f"job error: {error or row['error']}"
    assert set(row["domain_status"].values()) == {"DONE"}, row["domain_status"]


def test_pipeline_keeps_other_domains_when_one_domain_keeps_failing() -> None:
    gw = _FlakyGateway({"psychometric": -1})
    tenant_id, job_id, error = _run_flaky(gw)
    row, n_facts = _job(tenant_id, job_id)
    assert (error, row["status"]) == ("", "DONE"), (
        f"one failing domain out of six must not fail the job (5/6 partial accept); "
        f"job error: {error or row['error']}"
    )
    assert row["domain_status"]["psychometrics"].startswith("FAILED"), row["domain_status"]
    others = {d: s for d, s in row["domain_status"].items() if d != "psychometrics"}
    assert set(others.values()) == {"DONE"}, row["domain_status"]
    assert n_facts == 1, f"biography fact from the same chunk was not kept ({n_facts} facts)"


def test_pipeline_fails_job_when_two_domains_keep_failing() -> None:
    gw = _FlakyGateway({"psychometric": -1, "preference facts": -1})
    tenant_id, job_id, error = _run_flaky(gw)
    row, _ = _job(tenant_id, job_id)
    assert row["status"] == "FAILED", "two failing domains out of six must fail the job"
    assert "only 4/6 domains succeeded" in (row["error"] or ""), (
        f"job must fail on the partial-accept gate, not on the first LLM error; "
        f"error was: {row['error']}"
    )
    assert error == row["error"]


_PROMPT_KEYS = {
    "biography": "biographical", "experiences": "experience/event",
    "preferences": "preference facts", "psychometrics": "psychometric",
    "social_circle": "social relationship", "work": "work and career",
}


class _CountingGateway:
    """Fake LLM that counts calls per domain; domains in `failing` always raise."""

    def __init__(self, failing: frozenset[str] = frozenset()) -> None:
        self._failing = failing
        self._lock = threading.Lock()
        self.calls: dict[str, int] = dict.fromkeys(_PROMPT_KEYS, 0)

    def complete(self, *, tier: object, messages: list[dict[str, str]],
                 json_mode: bool, temperature: float = 0.0,
                 max_tokens: int = 2048) -> str:
        prompt = messages[0]["content"].lower()
        domain = next(d for d, key in _PROMPT_KEYS.items() if key in prompt)
        with self._lock:
            self.calls[domain] += 1
        if domain in self._failing:
            raise TimeoutError(f"LLM timed out ({domain})")
        if domain == "biography":
            return json.dumps({"birth_date_precision": "year"})
        return json.dumps({})


def _upload_once(  # type: ignore[explicit-any]
        tenant_id: str, persona_id: str, gw: _CountingGateway, raw: bytes,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Run one upload; return the job row and its stored facts counted per domain."""
    pipeline = IngestPipeline(
        gateway=gw,  # type: ignore[arg-type]
        failure_policy=ExtractionFailurePolicy(base_delay_s=0.0),
    )
    job_repo = IngestJobRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        asyncio.run(pipeline.run(conn=conn, tenant_id=tenant_id, persona_id=persona_id,
                                 job_id=job_id, fmt="whatsapp", raw=raw))
        row = job_repo.get_job(conn, tenant_id, job_id)
        assert row is not None
        per_domain: dict[str, int] = {}
        for f in PendingFactRepository().list_for_job(conn, tenant_id, job_id):
            per_domain[f["domain"]] = per_domain.get(f["domain"], 0) + 1
        return row, per_domain
    finally:
        gen.close()


def test_reupload_after_one_domain_failed_extracts_only_that_domain() -> None:
    """US-2.7 accepts a chunk with 5/6 domains; US-2.3 forbids duplicate facts.

    So a re-upload must run the domain that failed, and only that domain.
    """
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    raw = (b"[2026-04-21 12:00] Alice: I was born in 1990.\n"
           b"[2026-04-21 12:01] Alice: I grew up in Lisbon.\n")

    row1, facts1 = _upload_once(
        tenant_id, persona_id, _CountingGateway(frozenset({"psychometrics"})), raw)
    assert row1["status"] == "DONE", row1["error"]
    assert row1["domain_status"]["psychometrics"].startswith("FAILED"), row1["domain_status"]
    assert facts1 == {"biography": 1}, facts1

    gw2 = _CountingGateway()
    row2, facts2 = _upload_once(tenant_id, persona_id, gw2, raw)
    assert row2["status"] == "DONE", row2["error"]
    assert gw2.calls["psychometrics"] > 0, (
        "re-upload did not extract psychometrics, the domain that failed the first time"
    )
    already_done = {d: n for d, n in gw2.calls.items() if d != "psychometrics" and n}
    assert already_done == {}, (
        f"re-upload extracted domains that already succeeded: {already_done}"
    )
    assert facts2 == {}, f"re-upload stored duplicate facts: {facts2}"

    gw3 = _CountingGateway()
    _, facts3 = _upload_once(tenant_id, persona_id, gw3, raw)
    assert sum(gw3.calls.values()) == 0, f"third upload called the LLM: {gw3.calls}"
    assert facts3 == {}, facts3


def test_message_recorded_before_per_domain_tracking_is_not_extracted_again() -> None:
    """Rows from before the domain column have domain '*': every domain processed them."""
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    raw = b"[2026-04-21 12:00] Alice: I was born in 1990.\n"
    msg = WhatsAppAdapter().parse(raw)[0]
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        PendingFactRepository().mark_seen(
            conn, tenant_id, persona_id, [IdempotencyGuard().hash_for(msg)], [ALL_DOMAINS],
        )
    finally:
        gen.close()

    gw = _CountingGateway()
    _, facts = _upload_once(tenant_id, persona_id, gw, raw)
    assert sum(gw.calls.values()) == 0, f"an already ingested message was extracted: {gw.calls}"
    assert facts == {}, facts


def test_domain_that_failed_in_an_earlier_chunk_is_reported_failed() -> None:
    """A later chunk's success must not hide an earlier chunk's failure (US-2.8, DIR-3.9).

    The failed chunk's messages are not recorded for that domain, so a
    re-upload extracts them again; the job must say so.
    """
    max_attempts = ExtractionFailurePolicy().max_attempts
    # Every psychometrics call in chunk 1 fails; the first call in chunk 2 succeeds.
    gw = _FlakyGateway({"psychometric": max_attempts})
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    raw = (b"[2026-04-21 12:00] Alice: I was born in 1990.\n"
           b"[2026-04-21 12:01] Alice: I grew up in Lisbon.\n")
    one_message = Chunker()._tokens(WhatsAppAdapter().parse(raw)[0])
    pipeline = IngestPipeline(
        gateway=gw,  # type: ignore[arg-type]
        chunker=Chunker(window_tokens=one_message + 1, overlap_tokens=0),
        failure_policy=ExtractionFailurePolicy(base_delay_s=0.0),
    )
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = IngestJobRepository().create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        asyncio.run(pipeline.run(conn=conn, tenant_id=tenant_id, persona_id=persona_id,
                                 job_id=job_id, fmt="whatsapp", raw=raw))
    finally:
        gen.close()
    row, _ = _job(tenant_id, job_id)
    assert gw.calls["psychometric"] == max_attempts + 1, (
        f"expected two chunks; psychometrics was called {gw.calls['psychometric']} time(s)"
    )
    assert row["status"] == "DONE", row["error"]
    assert row["domain_status"]["psychometrics"].startswith("FAILED"), (
        f"psychometrics failed in chunk 1 but the job shows {row['domain_status']}"
    )
    others = {d: s for d, s in row["domain_status"].items() if d != "psychometrics"}
    assert set(others.values()) == {"DONE"}, row["domain_status"]
