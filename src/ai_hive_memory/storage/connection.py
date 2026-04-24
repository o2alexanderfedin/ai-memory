"""Request-scoped Postgres connection with tenant_scope wired in.

Yields a SQLAlchemy Connection that has `app.current_tenant_id` set for the
caller's tenant. Used as a FastAPI dependency in per-tenant API handlers.
"""
from collections.abc import Generator
from contextlib import suppress

from sqlalchemy.engine import Connection

from ai_hive_memory.storage.db import get_engine
from ai_hive_memory.storage.rls import tenant_scope


def request_scoped_conn(tenant_id: str) -> Generator[Connection, None, None]:
    """Yield a Connection scoped to `tenant_id` for the duration of the request."""
    engine = get_engine()
    with engine.begin() as conn, tenant_scope(conn, tenant_id):  # noqa: SIM117
        # Suppress GeneratorExit so that outer context managers (__exit__) still
        # run to commit the transaction when generator.close() is called
        with suppress(GeneratorExit):
            yield conn
