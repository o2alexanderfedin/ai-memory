"""Verify tenant_scope correctly sets and resets app.current_tenant_id."""
from uuid import uuid4

from sqlalchemy import text

from synthius_mem.storage.db import get_engine
from synthius_mem.storage.rls import tenant_scope


def test_tenant_scope_sets_and_resets() -> None:
    engine = get_engine()
    tenant_id = str(uuid4())

    with engine.begin() as conn:
        with tenant_scope(conn, tenant_id):
            current = conn.execute(
                text("SELECT current_setting('app.current_tenant_id', true)")
            ).scalar()
            assert current == tenant_id

        # After the with block, value should be reset (empty string)
        current_after = conn.execute(
            text("SELECT current_setting('app.current_tenant_id', true)")
        ).scalar()
        assert current_after in ("", None), (
            f"tenant_scope did not reset: still {current_after!r}"
        )


def test_tenant_scope_resets_on_exception() -> None:
    engine = get_engine()
    tenant_id = str(uuid4())

    class _BoomError(Exception):
        pass

    with engine.begin() as conn:
        try:
            with tenant_scope(conn, tenant_id):
                raise _BoomError("simulated failure inside tenant scope")
        except _BoomError:
            pass

        current = conn.execute(
            text("SELECT current_setting('app.current_tenant_id', true)")
        ).scalar()
        assert current in ("", None), (
            f"tenant_scope did not reset on exception: still {current!r}"
        )
