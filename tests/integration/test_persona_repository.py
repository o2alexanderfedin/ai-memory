"""PersonaRepository tenant-scoped CRUD."""
from uuid import uuid4

from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.repository import PersonaRepository

ULID_LEN = 26


def test_create_persona_returns_ulid() -> None:
    tenant_id = str(uuid4())
    repo = PersonaRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        persona_id = repo.create_persona(conn, tenant_id)
        assert isinstance(persona_id, str)
        assert len(persona_id) == ULID_LEN
    finally:
        gen.close()


def test_list_personas_returns_only_current_tenant() -> None:
    tenant_a = str(uuid4())
    tenant_b = str(uuid4())
    repo = PersonaRepository()

    # Seed under tenant_a
    gen_a = request_scoped_conn(tenant_a)
    conn_a = next(gen_a)
    try:
        repo.create_persona(conn_a, tenant_a)
        repo.create_persona(conn_a, tenant_a)
    finally:
        gen_a.close()

    # Seed under tenant_b
    gen_b = request_scoped_conn(tenant_b)
    conn_b = next(gen_b)
    try:
        repo.create_persona(conn_b, tenant_b)
    finally:
        gen_b.close()

    # tenant_a sees 2; tenant_b sees 1
    gen_a2 = request_scoped_conn(tenant_a)
    conn_a2 = next(gen_a2)
    try:
        rows_a = repo.list_personas(conn_a2)
        assert len(rows_a) == 2  # noqa: PLR2004 — semantic count from seeding above
    finally:
        gen_a2.close()

    gen_b2 = request_scoped_conn(tenant_b)
    conn_b2 = next(gen_b2)
    try:
        rows_b = repo.list_personas(conn_b2)
        assert len(rows_b) == 1
    finally:
        gen_b2.close()
