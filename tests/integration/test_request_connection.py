"""Verify request_scoped_conn yields a Connection inside a tenant_scope."""
from uuid import uuid4

from sqlalchemy import text

from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.db import get_engine


def test_request_scoped_conn_sets_tenant_id_inside_scope() -> None:
    tenant_id = str(uuid4())
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        current = conn.execute(
            text("SELECT current_setting('app.current_tenant_id', true)")
        ).scalar()
        assert current == tenant_id
    finally:
        gen.close()


def test_request_scoped_conn_resets_tenant_id_after_scope() -> None:
    tenant_id = str(uuid4())
    gen = request_scoped_conn(tenant_id)
    next(gen)
    gen.close()  # triggers the finally block

    # New connection should NOT have the prior tenant_id
    with get_engine().connect() as conn2:
        current = conn2.execute(
            text("SELECT current_setting('app.current_tenant_id', true)")
        ).scalar()
        assert current in ("", None), f"tenant_id leaked across connections: {current!r}"
