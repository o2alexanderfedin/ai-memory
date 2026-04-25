"""Persona-level repository: tenant-scoped CRUD for the personas table.

All methods take a Connection that ALREADY has app.current_tenant_id set
(via request_scoped_conn). RLS does the cross-tenant deny.
"""
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ulid import ULID


class PersonaRepository:
    """Persona-level CRUD operations.

    Stateless — methods take the Connection. One repository instance per process
    is sufficient; no per-tenant state lives in the repository.
    """

    def create_persona(self, conn: Connection, tenant_id: str) -> str:
        """Insert a new persona row under the current tenant scope. Returns the ULID."""
        persona_id = str(ULID())
        conn.execute(
            text("""
                INSERT INTO personas (tenant_id, persona_id)
                VALUES (:tid, :pid)
            """),
            {"tid": tenant_id, "pid": persona_id},
        )
        return persona_id

    def list_personas(self, conn: Connection) -> list[str]:
        """Return persona_ids visible to the current tenant scope (RLS-enforced)."""
        rows = conn.execute(
            text("SELECT persona_id FROM personas ORDER BY created_at ASC")
        ).fetchall()
        return [row[0] for row in rows]
