"""IngestJobRepository + PendingFactRepository — tenant-scoped CRUD."""
from datetime import UTC, datetime
from uuid import uuid4

from ai_hive_memory.schemas.biography import Biography, BiographyFields
from ai_hive_memory.schemas.envelope import CommonEnvelope, Provenance
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


def _make_biography_fact(persona_id: str) -> Biography:
    now = datetime.now(UTC)
    return Biography(
        envelope=CommonEnvelope(
            persona_id=persona_id,
            domain="biography",
            schema_version="1.0",
            confidence=0.9,
            provenance=Provenance(
                source_message_id=str(uuid4()),
                source_chunk_id=str(uuid4()),
                extracted_at=now,
                extractor_version="epic2-mvp",
            ),
            created_at=now,
            updated_at=now,
        ),
        fields=BiographyFields(),
    )


def test_create_job_returns_uuid_and_persists() -> None:
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    job_repo = IngestJobRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        row = job_repo.get_job(conn, tenant_id, job_id)
        assert row is not None
        assert row["status"] == "PENDING"
        assert row["format"] == "whatsapp"
        assert row["persona_id"] == persona_id
    finally:
        gen.close()


def test_update_job_status_persists() -> None:
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    job_repo = IngestJobRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        job_repo.update_status(conn, tenant_id, job_id, status="DONE",
                               domain_status={"biography": "DONE"})
        row = job_repo.get_job(conn, tenant_id, job_id)
        assert row is not None
        assert row["status"] == "DONE"
        assert row["domain_status"] == {"biography": "DONE"}
    finally:
        gen.close()


def test_persist_pending_fact_round_trips() -> None:
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    job_repo = IngestJobRepository()
    pf_repo = PendingFactRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        fact = _make_biography_fact(persona_id)
        pf_repo.persist(conn, tenant_id, persona_id, job_id,
                        domain="biography", fact=fact, source_hash="0" * 64)
        all_facts = pf_repo.list_for_job(conn, tenant_id, job_id)
        assert len(all_facts) == 1
        assert all_facts[0]["domain"] == "biography"
    finally:
        gen.close()


def test_seen_domains_for_persona_returns_persisted_hashes_with_their_domain() -> None:
    tenant_id = str(uuid4())
    persona_id = _bootstrap_persona(tenant_id)
    job_repo = IngestJobRepository()
    pf_repo = PendingFactRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        job_id = job_repo.create_job(conn, tenant_id, persona_id, fmt="whatsapp")
        fact = _make_biography_fact(persona_id)
        pf_repo.persist(conn, tenant_id, persona_id, job_id,
                        domain="biography", fact=fact, source_hash="abc123")
        seen = pf_repo.seen_domains_for_persona(conn, tenant_id, persona_id)
        assert seen == {"abc123": {"biography"}}
    finally:
        gen.close()
