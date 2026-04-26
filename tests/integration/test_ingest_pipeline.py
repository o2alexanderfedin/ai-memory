"""IngestPipeline orchestrator — wires adapter → idempotency → PII → chunker → fanout → persist."""
import asyncio
import json
from unittest.mock import MagicMock
from uuid import uuid4

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
