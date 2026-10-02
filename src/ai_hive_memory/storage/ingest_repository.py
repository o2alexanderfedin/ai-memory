"""Tenant-scoped repositories for ingest_jobs + pending_facts."""
import json
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

_NUL = "\x00"
ALL_DOMAINS = "*"  # ingested_messages.domain of rows that cover every domain


def _without_nul(value: object) -> object:
    """Remove NUL characters from every string in a JSON-ready value.

    Postgres text and jsonb cannot store NUL ("\\u0000"); one NUL anywhere in
    a fact, for example copied from the uploaded message text, would make
    the insert fail. A NUL carries no meaning in a conversation.
    """
    if isinstance(value, str):
        return value.replace(_NUL, "")
    if isinstance(value, list):
        return [_without_nul(v) for v in value]
    if isinstance(value, dict):
        return {str(_without_nul(k)): _without_nul(v) for k, v in value.items()}
    return value


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
                "ds": json.dumps(_without_nul(domain_status or {})),
                "err": None if error is None else error.replace(_NUL, ""),
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
                "payload": json.dumps(_without_nul(fact.model_dump(mode="json"))),
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

    def seen_domains_for_persona(self, conn: Connection, tenant_id: str,
                                 persona_id: str) -> dict[str, set[str]]:
        """Map each ingested message hash to the domains that processed it.

        ALL_DOMAINS ('*') stands for every domain (rows from before domains
        were recorded).
        """
        # pending_facts.source_hash still counts, for its own domain: rows
        # written before ingested_messages existed are the only record of
        # those messages.
        rows = conn.execute(
            text("""
                SELECT message_hash, domain FROM ingested_messages
                WHERE tenant_id = :tid AND persona_id = :pid
                UNION
                SELECT source_hash, domain FROM pending_facts
                WHERE tenant_id = :tid AND persona_id = :pid
            """),
            {"tid": tenant_id, "pid": persona_id},
        ).fetchall()
        seen: dict[str, set[str]] = {}
        for message_hash, domain in rows:
            seen.setdefault(message_hash, set()).add(domain)
        return seen

    def mark_seen(self, conn: Connection, tenant_id: str, persona_id: str,
                  message_hashes: list[str], domains: list[str]) -> None:
        """Record that `domains` processed every message, so a re-upload skips them."""
        if not message_hashes or not domains:
            return
        conn.execute(
            text("""
                INSERT INTO ingested_messages (tenant_id, persona_id, message_hash, domain)
                VALUES (:tid, :pid, :hash, :domain)
                ON CONFLICT DO NOTHING
            """),
            [{"tid": tenant_id, "pid": persona_id, "hash": h, "domain": d}
             for h in message_hashes for d in domains],
        )
