"""RLS context-setter — wraps each request scope (DIR-2.3, DIR-11.1)."""
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.engine import Connection


@contextmanager
def tenant_scope(conn: Connection, tenant_id: str) -> Iterator[None]:
    """Set app.current_tenant_id for the duration of this connection's transaction."""
    conn.execute(text("SET app.current_tenant_id = :tid"), {"tid": tenant_id})
    try:
        yield
    finally:
        conn.execute(text("RESET app.current_tenant_id"))
