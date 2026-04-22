"""Force RLS on table owners — required so service role doesn't bypass.

Creates a dedicated synthius_app role (no superuser, no BYPASSRLS) for the
application connection so RLS policies are genuinely enforced at runtime.
FORCE ROW LEVEL SECURITY ensures even table owners cannot bypass policies.

Revision ID: dd86529079db
Revises: 5db854d514f2
Create Date: 2026-04-21 21:42:08.302982
"""
from collections.abc import Sequence

from alembic import op

revision: str = "dd86529079db"
down_revision: str | Sequence[str] | None = "5db854d514f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES = (
    "biography", "experiences", "preferences",
    "social_circle", "work", "psychometrics", "wal",
)


def upgrade() -> None:
    # FORCE RLS so even the table-owning role cannot bypass policies.
    for t in _TABLES:
        op.execute(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY;")

    # Harden the tenant_isolation policy: use NULLIF so that an empty/missing
    # app.current_tenant_id becomes NULL instead of raising a cast error.
    # NULL = tenant_id is always false → zero rows returned (safe default).
    for t in _TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {t};")
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {t}
            USING (
                tenant_id = NULLIF(
                    current_setting('app.current_tenant_id', true), ''
                )::uuid
            );
        """)

    # Create a dedicated app role without SUPERUSER / BYPASSRLS so that RLS
    # is genuinely enforced for all application queries.
    op.execute(
        "DO $$ BEGIN "
        "  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'synthius_app') "
        "  THEN CREATE ROLE synthius_app LOGIN PASSWORD 'dev_only_password' "
        "              NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS; "
        "  END IF; "
        "END $$;"
    )
    for t in _TABLES:
        op.execute(
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON {t} TO synthius_app;"
        )
    op.execute("GRANT USAGE ON SCHEMA public TO synthius_app;")


def downgrade() -> None:
    op.execute(
        "DO $$ BEGIN "
        "  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'synthius_app') THEN "
        + " ".join(
            f"REVOKE SELECT, INSERT, UPDATE, DELETE ON {t} FROM synthius_app; "
            for t in _TABLES
        )
        + "  REVOKE USAGE ON SCHEMA public FROM synthius_app; "
        "  DROP ROLE synthius_app; "
        "  END IF; "
        "END $$;"
    )
    for t in _TABLES:
        op.execute(f"ALTER TABLE {t} NO FORCE ROW LEVEL SECURITY;")
