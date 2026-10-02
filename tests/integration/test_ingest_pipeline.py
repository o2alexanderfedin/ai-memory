"""IngestPipeline orchestrator — wires adapter → idempotency → PII → chunker → fanout → persist."""
import asyncio
import json
import threading
from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

from ai_hive_memory.ingest.failure_policy import ExtractionFailurePolicy
from ai_hive_memory.ingest.pipeline import IngestPipeline
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.ingest_repository import (
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
