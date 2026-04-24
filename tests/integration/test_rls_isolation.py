"""LOAD-BEARING: prove cross-tenant data isolation under RLS (DIR-11.1).

This test is the single most important integrity check in the system.
If it ever fails, do NOT ship — one bug = total cross-tenant data breach.
"""
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection
from ulid import ULID

from ai_hive_memory.storage.db import get_engine


def _seed_fact(conn: Connection, tenant_id: str, persona_id: str, fact_id: str) -> None:
    conn.execute(
        text("""
            INSERT INTO biography
              (tenant_id, persona_id, fact_id, schema_version, fields, envelope)
            VALUES
              (:tid, :pid, :fid, '1.0.0', '{}'::jsonb, '{}'::jsonb)
        """),
        {"tid": tenant_id, "pid": persona_id, "fid": fact_id},
    )


def test_tenant_a_cannot_read_tenant_b_persona() -> None:
    engine = get_engine()
    tenant_a = str(uuid4())
    tenant_b = str(uuid4())
    persona_b = str(ULID())
    fact_b = str(uuid4())

    with engine.begin() as conn:
        # Seed under tenant_b context
        conn.execute(text(f"SET app.current_tenant_id = '{tenant_b}';"))
        _seed_fact(conn, tenant_b, persona_b, fact_b)

    with engine.begin() as conn:
        # Query under tenant_a context — should see ZERO rows
        conn.execute(text(f"SET app.current_tenant_id = '{tenant_a}';"))
        rows = conn.execute(
            text("SELECT fact_id FROM biography WHERE persona_id = :pid"),
            {"pid": persona_b},
        ).fetchall()
        assert rows == [], (
            f"RLS BREACH: tenant_a saw tenant_b's data. Rows: {rows}"
        )

    with engine.begin() as conn:
        # Sanity: tenant_b CAN see its own data
        conn.execute(text(f"SET app.current_tenant_id = '{tenant_b}';"))
        rows = conn.execute(
            text("SELECT fact_id FROM biography WHERE persona_id = :pid"),
            {"pid": persona_b},
        ).fetchall()
        assert len(rows) == 1, "tenant_b should see its own seeded row"


def test_no_tenant_context_set_returns_empty() -> None:
    """Without setting app.current_tenant_id, RLS denies all rows."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("RESET app.current_tenant_id;"))
        rows = conn.execute(text("SELECT * FROM biography LIMIT 1")).fetchall()
        assert rows == []
