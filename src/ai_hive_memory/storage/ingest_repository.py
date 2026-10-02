"""Tenant-scoped repositories for ingest_jobs + pending_facts."""
import json
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection


class IngestJobRepository:
    """CRUD for the ingest_jobs table."""

    def create_job(self, conn: Connection, tenant_id: str, persona_id: str, *,
                   fmt: str) -> str:
        job_id = str(uuid4())
        conn.execute(
            text("""
                INSERT INTO ingest_jobs (tenant_id, job_id, persona_id, format, status)
                VALUES (:tid, :jid, :pid, :fmt, 'PENDING')
            """),
            {"tid": tenant_id, "jid": job_id, "pid": persona_id, "fmt": fmt},
        )
        return job_id

    def update_status(  # noqa: PLR0913
            self, conn: Connection, tenant_id: str, job_id: str, *,
            status: str, domain_status: dict[str, str] | None = None,
            error: str | None = None) -> None:
        conn.execute(
            text("""
                UPDATE ingest_jobs
                SET status = :status,
                    domain_status = CAST(:ds AS jsonb),
                    error = :err,
                    updated_at = now()
                WHERE tenant_id = :tid AND job_id = :jid
            """),
            {
                "tid": tenant_id, "jid": job_id, "status": status,
                "ds": json.dumps(domain_status or {}),
                "err": error,
            },
        )

    def get_job(self, conn: Connection, tenant_id: str, job_id: str) -> dict[str, Any] | None:  # type: ignore[explicit-any]
        row = conn.execute(
            text("""
                SELECT job_id::text, persona_id, format, status, domain_status, error,
                       created_at, updated_at
                FROM ingest_jobs
                WHERE tenant_id = :tid AND job_id = :jid
            """),
            {"tid": tenant_id, "jid": job_id},
        ).mappings().fetchone()
        return dict(row) if row else None


class PendingFactRepository:
    """CRUD for the pending_facts table."""

    def persist(  # noqa: PLR0913
            self, conn: Connection, tenant_id: str, persona_id: str,
            job_id: str, *, domain: str, fact: BaseModel,
            source_hash: str) -> str:
        pending_fact_id = str(uuid4())
        conn.execute(
            text("""
                INSERT INTO pending_facts
                  (tenant_id, persona_id, pending_fact_id, job_id, domain,
                   payload, source_hash)
                VALUES (:tid, :pid, :pfid, :jid, :domain, CAST(:payload AS jsonb), :hash)
            """),
            {
                "tid": tenant_id, "pid": persona_id, "pfid": pending_fact_id,
                "jid": job_id, "domain": domain,
                "payload": fact.model_dump_json(),
                "hash": source_hash,
            },
        )
        return pending_fact_id

    def list_for_job(  # type: ignore[explicit-any]
            self, conn: Connection, tenant_id: str,
            job_id: str) -> list[dict[str, Any]]:
        rows = conn.execute(
            text("""
                SELECT pending_fact_id::text, domain, payload, source_hash
                FROM pending_facts
                WHERE tenant_id = :tid AND job_id = :jid
                ORDER BY created_at ASC
            """),
            {"tid": tenant_id, "jid": job_id},
        ).mappings().fetchall()
        return [dict(r) for r in rows]

    def seen_hashes_for_persona(self, conn: Connection, tenant_id: str,
                                persona_id: str) -> set[str]:
        # pending_facts.source_hash still counts: rows written before
        # ingested_messages existed are the only record of those messages.
        rows = conn.execute(
            text("""
                SELECT message_hash FROM ingested_messages
                WHERE tenant_id = :tid AND persona_id = :pid
                UNION
                SELECT source_hash FROM pending_facts
                WHERE tenant_id = :tid AND persona_id = :pid
            """),
            {"tid": tenant_id, "pid": persona_id},
        ).fetchall()
        return {r[0] for r in rows}

    def mark_seen(self, conn: Connection, tenant_id: str, persona_id: str,
                  message_hashes: list[str]) -> None:
        """Record every processed message so a re-upload skips all of them."""
        if not message_hashes:
            return
        conn.execute(
            text("""
                INSERT INTO ingested_messages (tenant_id, persona_id, message_hash)
                VALUES (:tid, :pid, :hash)
                ON CONFLICT DO NOTHING
            """),
            [{"tid": tenant_id, "pid": persona_id, "hash": h} for h in message_hashes],
        )
