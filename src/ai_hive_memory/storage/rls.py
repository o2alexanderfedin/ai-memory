"""RLS context-setter — wraps each request scope (DIR-2.3, DIR-11.1)."""
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.engine import Connection


@contextmanager
def tenant_scope(conn: Connection, tenant_id: str) -> Iterator[None]:
    """Set `app.current_tenant_id` for the duration of this connection's transaction.

    Uses Postgres `set_config(name, value, is_local=true)` — accepts prepared-statement
    parameters (unlike the SQL `SET` command which does not). `is_local=true` scopes the
    setting to the current transaction; on commit/rollback it reverts automatically.
    """
    conn.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": tenant_id},
    )
    try:
        yield
    finally:
        # Explicit RESET is no-op when the transaction has already ended
        # (set_config with is_local=true reverts on commit/rollback). Kept for
        # the rare case where the caller is using a long-lived connection
        # outside a transaction context.
        conn.execute(text("SELECT set_config('app.current_tenant_id', '', false)"))
