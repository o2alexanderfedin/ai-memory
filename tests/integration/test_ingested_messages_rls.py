"""LOAD-BEARING: tenant_a cannot read or write tenant_b's ingested_messages (DIR-11.1).

ingested_messages holds the hash of every message a persona has ingested. A
leak would tell one tenant which messages another tenant uploaded; a foreign
insert would make another tenant's next upload silently skip those messages.
"""
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from ai_hive_memory.storage.db import get_engine
from ai_hive_memory.storage.ingest_repository import PendingFactRepository
from ai_hive_memory.storage.rls import tenant_scope

PERSONA = "01HZZZZZZZZZZZZZZZZZZZZZZZ"


def _count_rows(tenant_id: str, owner_tenant_id: str) -> int:
    """Rows of `owner_tenant_id` visible while scoped to `tenant_id`."""
    with get_engine().begin() as conn, tenant_scope(conn, tenant_id):
        return int(conn.execute(
            text("SELECT count(*) FROM ingested_messages WHERE tenant_id = :tid"),
            {"tid": owner_tenant_id},
        ).scalar_one())


def test_tenant_a_cannot_read_tenant_b_ingested_messages() -> None:
    tenant_a, tenant_b = str(uuid4()), str(uuid4())
    repo = PendingFactRepository()
    with get_engine().begin() as conn, tenant_scope(conn, tenant_b):
        repo.mark_seen(conn, tenant_b, PERSONA, ["b" * 64])

    # Sanity: tenant_b sees its own row.
    assert _count_rows(tenant_b, tenant_b) == 1

    assert _count_rows(tenant_a, tenant_b) == 0, "RLS BREACH: tenant_a saw tenant_b's rows"
    with get_engine().begin() as conn, tenant_scope(conn, tenant_a):
        seen = repo.seen_hashes_for_persona(conn, tenant_b, PERSONA)
    assert seen == set(), f"RLS BREACH: tenant_a saw tenant_b's hashes {seen}"


def test_tenant_a_cannot_insert_into_tenant_b_ingested_messages() -> None:
    tenant_a, tenant_b = str(uuid4()), str(uuid4())
    repo = PendingFactRepository()
    with (
        get_engine().begin() as conn,
        tenant_scope(conn, tenant_a),
        pytest.raises(DBAPIError, match="row-level security"),
        conn.begin_nested(),
    ):
        repo.mark_seen(conn, tenant_b, PERSONA, ["a" * 64])

    assert _count_rows(tenant_b, tenant_b) == 0, (
        "RLS BREACH: tenant_a wrote a row into tenant_b's ingested_messages"
    )
