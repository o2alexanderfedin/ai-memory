# Epic 1: Onboard Persona Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Authenticated tenants can sign up with scope attestations, create personas under their tenant, and list only their own personas — with cross-tenant isolation proven load-bearing.

**Architecture:** Three new tables (`tenants`, `personas`, `scope_attestations`) extend the existing 6-domain schema with persona ownership + Decision 12 MVP compliance. Two new endpoints (`POST /signup` and `POST/GET /personas`) wire `tenant_scope` from Epic 0 into per-request connection management. IP geo-block uses an interface-only stub at MVP (real MaxMind integration deferred per Decision 12).

**Tech Stack:** Same as Epic 0 — Python 3.12 + FastAPI + Pydantic v2 + Postgres 15 + SQLAlchemy 2 Core + Alembic + LiteLLM (unused by E1) + pytest + ruff + mypy strict. No new dependencies.

**Slice mapping:** Implements vertical slice S-1 (Onboard Persona) per `docs/architecture/ARCHITECTURE.md` §3 + Decision 12 MVP-mandatory scope-exclusion enforcement.

**Success criteria (epic-level):** all of the following succeed:
1. `uv run pytest -q` → all tests pass (estimate: 43 prior + ~14 new + 1 skipped = 58 total)
2. `POST /signup` with valid attestations creates a tenant + returns a JWT
3. `POST /signup` with missing or false attestations returns 422
4. `POST /personas` (with valid token) creates a persona under the current tenant + returns the ULID
5. `GET /personas` (with valid token) returns ONLY the current tenant's personas
6. `tests/integration/test_personas_rls.py` proves tenant-A cannot see tenant-B's personas via the API (load-bearing)
7. ruff + mypy strict still clean

---

## File structure

```
src/synthius_mem/
├── storage/
│   ├── tables.py                          # MODIFY: add tenants, personas, scope_attestations
│   ├── connection.py                      # NEW: request_scoped_conn FastAPI dep
│   └── repository.py                      # NEW: PersonaRepository (tenant-scoped CRUD)
├── auth/
│   ├── scope_attestation.py               # NEW: ScopeAttestation Pydantic model
│   └── geoip.py                           # NEW: IPGeoBlocker interface + no-op impl
├── api/
│   ├── personas.py                        # NEW: POST + GET /personas router
│   └── signup_routes.py                   # NEW: POST /signup
└── main.py                                # MODIFY: remove /personas stub; include new routers

alembic/versions/
└── 0003_*_tenants_personas_attestations.py  # NEW: 3 new tables

tests/
├── unit/
│   ├── test_scope_attestation.py          # NEW: attestation validation
│   └── test_geoip.py                      # NEW: IPGeoBlocker contract
├── integration/
│   ├── test_personas.py                   # NEW: POST + GET happy-path
│   ├── test_signup.py                     # NEW: signup flow + attestation enforcement
│   └── test_personas_rls.py               # NEW: load-bearing cross-tenant API isolation
```

---

## Task 1: Schema additions (tables.py + Alembic generation)

**Files:**
- Modify: `src/synthius_mem/storage/tables.py` (append 3 Table definitions)
- Test: `tests/integration/test_db_indexes.py:1-50` (extend with assertions for new tables)

- [ ] **Step 1: Extend `tests/integration/test_db_indexes.py` with new assertions**

Append to the existing test file:

```python
def test_metadata_has_tenants_personas_attestations() -> None:
    table_names = {t.name for t in metadata.sorted_tables}
    expected = {"tenants", "personas", "scope_attestations"}
    assert expected.issubset(table_names)


def test_personas_has_composite_pk_tenant_persona() -> None:
    """personas table PK is (tenant_id, persona_id) — one persona row per (tenant, persona)."""
    table = metadata.tables["personas"]
    pk_cols = [c.name for c in table.primary_key.columns]
    assert pk_cols == ["tenant_id", "persona_id"]


def test_tenants_has_pk_tenant_id() -> None:
    table = metadata.tables["tenants"]
    pk_cols = [c.name for c in table.primary_key.columns]
    assert pk_cols == ["tenant_id"]


def test_scope_attestations_has_pk_tenant_id() -> None:
    """One attestation record per tenant (overwritten on re-attestation)."""
    table = metadata.tables["scope_attestations"]
    pk_cols = [c.name for c in table.primary_key.columns]
    assert pk_cols == ["tenant_id"]
```

- [ ] **Step 2: Run tests, verify FAIL**

Run: `uv run pytest tests/integration/test_db_indexes.py -v -k 'tenants or personas or scope_attestations'`
Expected: 4 new tests FAIL with `KeyError: 'tenants'` (tables don't exist yet in metadata).

- [ ] **Step 3: Append tables to `src/synthius_mem/storage/tables.py`**

After the existing `wal` Table definition, append:

```python
# Tenants table — one row per tenant (DIR-11.1 + Decision 12 MVP)
tenants = Table(
    "tenants",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("created_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("tos_version", String, nullable=False),  # ToS version the tenant accepted at signup
    PrimaryKeyConstraint("tenant_id", name="pk_tenants"),
)


# Personas table — canonical persona record per (tenant, persona)
# (Domain-fact tables reference (tenant_id, persona_id) but don't FK; persona must
# exist here before any facts can be written — enforced at the application layer.)
personas = Table(
    "personas",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("persona_id", String(26), nullable=False),  # ULID
    Column("created_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("updated_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    PrimaryKeyConstraint("tenant_id", "persona_id", name="pk_personas"),
)


# Scope attestations — Decision 12 MVP customer-scope exclusions, recorded at signup
scope_attestations = Table(
    "scope_attestations",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("attested_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("no_phi", Boolean, nullable=False),
    Column("no_payment_data", Boolean, nullable=False),
    Column("no_minors", Boolean, nullable=False),
    Column("no_eu_uk_residents", Boolean, nullable=False),
    Column("no_sensitive_categories", Boolean, nullable=False),
    Column("source_ip", String(45), nullable=True),  # IPv4 or IPv6 string
    Column("source_country", String(2), nullable=True),  # ISO-3166 alpha-2 (or null)
    PrimaryKeyConstraint("tenant_id", name="pk_scope_attestations"),
)
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_db_indexes.py -v`
Expected: all 7 tests pass (3 prior + 4 new).

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/storage/tables.py tests/integration/test_db_indexes.py
git commit -m "feat(storage): add tenants/personas/scope_attestations table defs (Epic 1 schema)"
```

---

## Task 2: Alembic migration for new tables (apply to live DB)

**Files:**
- Create: `alembic/versions/0003_<hash>_tenants_personas_attestations.py`

- [ ] **Step 1: Generate the migration**

Run: `uv run alembic revision --autogenerate -m "tenants personas scope_attestations"`
Expected: creates `alembic/versions/<hash>_tenants_personas_scope_attestations.py` with autogenerated `op.create_table(...)` for the 3 new tables.

- [ ] **Step 2: Augment migration with RLS + FORCE RLS + grants for synthius_app**

Edit the generated file's `upgrade()` to APPEND after the autogenerated `op.create_table(...)` calls:

```python
    # DIR-2.3 + DIR-11.1: enable + force RLS + tenant_isolation policy on the 3 new tables
    for t in ("tenants", "personas", "scope_attestations"):
        op.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {t}
            USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
        """)

    # Grant DML to synthius_app (the non-superuser role from Task 9)
    for t in ("tenants", "personas", "scope_attestations"):
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {t} TO synthius_app;")
```

Edit `downgrade()` to PREPEND before the autogenerated drops:

```python
    for t in ("tenants", "personas", "scope_attestations"):
        op.execute(f"REVOKE ALL ON {t} FROM synthius_app;")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {t};")
        op.execute(f"ALTER TABLE {t} NO FORCE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY;")
```

- [ ] **Step 3: Apply the migration**

Run: `uv run alembic upgrade head`
Expected: `Running upgrade 5db854d514f2 -> <new_hash>, tenants personas scope_attestations` (or chain through the FORCE-RLS migration if its revision ID is higher).

- [ ] **Step 4: Verify tables + RLS live**

Run: `docker-compose exec -T postgres psql -U synthius -d synthius_mem -c "\dt"`
Expected: shows 11 tables (8 prior + tenants + personas + scope_attestations).

Run: `docker-compose exec -T postgres psql -U synthius -d synthius_mem -c "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname IN ('tenants','personas','scope_attestations') ORDER BY relname;"`
Expected: 3 rows, all with `t / t`.

- [ ] **Step 5: Verify down/up cycle is idempotent**

Run: `uv run alembic downgrade -1 && uv run alembic upgrade head`
Expected: no errors. The `0002 force_rls_on_owner` migration's `wal_op` cleanup is in the `0001_initial_schema_with_rls` migration; this new migration only drops what it created.

- [ ] **Step 6: Commit**

```bash
git add alembic/versions/
git commit -m "feat(storage): Alembic migration for tenants/personas/scope_attestations + RLS"
```

---

## Task 3: Request-scoped connection dependency

**Files:**
- Create: `src/synthius_mem/storage/connection.py`
- Test: `tests/integration/test_request_connection.py`

- [ ] **Step 1: Write the failing test**

`tests/integration/test_request_connection.py`:

```python
"""Verify request_scoped_conn yields a Connection inside a tenant_scope."""
from uuid import uuid4

from sqlalchemy import text

from synthius_mem.storage.connection import request_scoped_conn


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
    conn = next(gen)
    gen.close()  # triggers the finally block

    # New connection should NOT have the prior tenant_id
    from synthius_mem.storage.db import get_engine
    with get_engine().connect() as conn2:
        current = conn2.execute(
            text("SELECT current_setting('app.current_tenant_id', true)")
        ).scalar()
        assert current in ("", None), f"tenant_id leaked across connections: {current!r}"
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/integration/test_request_connection.py -v`
Expected: `ImportError: cannot import name 'request_scoped_conn' from 'synthius_mem.storage.connection'`

- [ ] **Step 3: Implement `connection.py`**

`src/synthius_mem/storage/connection.py`:

```python
"""Request-scoped Postgres connection with tenant_scope wired in.

Yields a SQLAlchemy Connection that has `app.current_tenant_id` set for the
caller's tenant. Used as a FastAPI dependency in per-tenant API handlers.
"""
from collections.abc import Iterator

from sqlalchemy.engine import Connection

from synthius_mem.storage.db import get_engine
from synthius_mem.storage.rls import tenant_scope


def request_scoped_conn(tenant_id: str) -> Iterator[Connection]:
    """Yield a Connection scoped to `tenant_id` for the duration of the request.

    Use as a FastAPI dependency:
        @router.get("/items")
        def list_items(claims: CurrentTenant) -> list[Item]:
            with next(request_scoped_conn(claims.tenant_id)) as conn:
                ...

    Or wire as a Depends(...) factory in a higher-order helper.
    """
    engine = get_engine()
    with engine.begin() as conn:
        with tenant_scope(conn, tenant_id):
            yield conn
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_request_connection.py -v`
Expected: `2 passed`.

- [ ] **Step 5: Run full suite to ensure no regressions**

Run: `uv run pytest -q`
Expected: still all green (43 prior + 4 new from Task 1 + 2 new from Task 3 = 49).

- [ ] **Step 6: Commit**

```bash
git add src/synthius_mem/storage/connection.py tests/integration/test_request_connection.py
git commit -m "feat(storage): request_scoped_conn dependency wraps engine + tenant_scope"
```

---

## Task 4: PersonaRepository (tenant-scoped CRUD)

**Files:**
- Create: `src/synthius_mem/storage/repository.py`
- Test: `tests/integration/test_persona_repository.py`

- [ ] **Step 1: Write the failing test**

`tests/integration/test_persona_repository.py`:

```python
"""PersonaRepository tenant-scoped CRUD."""
from uuid import uuid4

import pytest
from sqlalchemy import text

from synthius_mem.storage.connection import request_scoped_conn
from synthius_mem.storage.repository import PersonaRepository


def test_create_persona_returns_ulid() -> None:
    tenant_id = str(uuid4())
    repo = PersonaRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        persona_id = repo.create_persona(conn, tenant_id)
        assert isinstance(persona_id, str)
        assert len(persona_id) == 26  # ULID is 26 chars
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
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/integration/test_persona_repository.py -v`
Expected: `ImportError: cannot import name 'PersonaRepository'`.

- [ ] **Step 3: Implement `repository.py`**

`src/synthius_mem/storage/repository.py`:

```python
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
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_persona_repository.py -v`
Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/storage/repository.py tests/integration/test_persona_repository.py
git commit -m "feat(storage): PersonaRepository with tenant-scoped create/list"
```

---

## Task 5: ScopeAttestation Pydantic model

**Files:**
- Create: `src/synthius_mem/auth/scope_attestation.py`
- Test: `tests/unit/test_scope_attestation.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_scope_attestation.py`:

```python
"""ScopeAttestation Pydantic model tests (Decision 12 MVP customer-scope exclusions)."""
import pytest
from pydantic import ValidationError

from synthius_mem.auth.scope_attestation import ScopeAttestation


def _all_true() -> dict:
    return {
        "no_phi": True,
        "no_payment_data": True,
        "no_minors": True,
        "no_eu_uk_residents": True,
        "no_sensitive_categories": True,
    }


def test_all_true_attestation_validates() -> None:
    att = ScopeAttestation.model_validate(_all_true())
    assert att.no_phi is True


def test_any_false_attestation_rejected() -> None:
    """Each scope-exclusion must be explicitly attested True (Decision 12)."""
    for field in ["no_phi", "no_payment_data", "no_minors",
                  "no_eu_uk_residents", "no_sensitive_categories"]:
        bad = _all_true() | {field: False}
        with pytest.raises(ValidationError):
            ScopeAttestation.model_validate(bad)


def test_missing_field_rejected() -> None:
    """All 5 attestations are required — missing one is an error."""
    bad = _all_true()
    del bad["no_phi"]
    with pytest.raises(ValidationError):
        ScopeAttestation.model_validate(bad)


def test_extra_field_rejected() -> None:
    """Closed schema — extra fields rejected (DIR-1.1 spirit applied to API DTOs)."""
    bad = _all_true() | {"unexpected_field": True}
    with pytest.raises(ValidationError):
        ScopeAttestation.model_validate(bad)
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/unit/test_scope_attestation.py -v`
Expected: `ImportError: cannot import name 'ScopeAttestation'`.

- [ ] **Step 3: Implement `scope_attestation.py`**

`src/synthius_mem/auth/scope_attestation.py`:

```python
"""ScopeAttestation — signup-time customer-scope exclusion record (Decision 12 MVP).

All five fields MUST be True for signup to proceed. If a tenant attests False
to any of them, signup is rejected (HTTP 422). This is the load-bearing
mechanism behind Decision 12's compliance scope reduction.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


def _must_be_true(value: bool, field_name: str) -> bool:
    if not value:
        raise ValueError(
            f"{field_name} must be True; signup blocked by Decision 12 scope exclusions"
        )
    return value


class ScopeAttestation(BaseModel):  # type: ignore[explicit-any]
    """Signup-time scope attestations. Each MUST be True (Decision 12)."""

    model_config = ConfigDict(extra="forbid")

    no_phi: Annotated[bool, Field(description="Will not ingest health/PHI data")]
    no_payment_data: Annotated[bool, Field(description="Will not ingest payment data")]
    no_minors: Annotated[bool, Field(description="Tenant is 18+ and will not ingest minors' data")]
    no_eu_uk_residents: Annotated[bool, Field(description="Tenant is not in EU/UK")]
    no_sensitive_categories: Annotated[
        bool, Field(description="Will not ingest GDPR Art. 9 sensitive categories")
    ]

    def model_post_init(self, _context: object) -> None:
        """Enforce all-True invariant after Pydantic validation."""
        for field_name in (
            "no_phi", "no_payment_data", "no_minors",
            "no_eu_uk_residents", "no_sensitive_categories",
        ):
            _must_be_true(getattr(self, field_name), field_name)
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/unit/test_scope_attestation.py -v`
Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/auth/scope_attestation.py tests/unit/test_scope_attestation.py
git commit -m "feat(auth): ScopeAttestation model — all 5 exclusions must attest True (Decision 12)"
```

---

## Task 6: IPGeoBlocker interface + no-op default impl

**Files:**
- Create: `src/synthius_mem/auth/geoip.py`
- Test: `tests/unit/test_geoip.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_geoip.py`:

```python
"""IPGeoBlocker interface contract + DefaultIPGeoBlocker behavior."""
import pytest

from synthius_mem.auth.geoip import (
    BlockedCountryError,
    DefaultIPGeoBlocker,
    IPGeoBlocker,
)


def test_default_impl_implements_interface() -> None:
    blocker = DefaultIPGeoBlocker()
    assert isinstance(blocker, IPGeoBlocker)


def test_default_blocker_returns_none_country_for_any_ip() -> None:
    """Default no-op impl: looks up nothing, returns country=None for every IP."""
    blocker = DefaultIPGeoBlocker()
    assert blocker.lookup_country("1.2.3.4") is None
    assert blocker.lookup_country("2001:db8::1") is None


def test_default_blocker_does_not_raise_for_eu_country() -> None:
    """Default impl never blocks (no .mmdb available; fail-open per MVP per Decision 12).

    Production: swap in MaxMindIPGeoBlocker which would raise BlockedCountryError
    for GB, DE, FR, etc.
    """
    blocker = DefaultIPGeoBlocker()
    # Should not raise — there's no real lookup happening
    blocker.assert_not_blocked("1.2.3.4", blocked_countries={"GB", "DE", "FR"})


def test_blocked_country_error_carries_iso_code() -> None:
    err = BlockedCountryError("GB")
    assert err.country_code == "GB"
    assert "GB" in str(err)
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/unit/test_geoip.py -v`
Expected: `ImportError: cannot import name 'IPGeoBlocker'`.

- [ ] **Step 3: Implement `geoip.py`**

`src/synthius_mem/auth/geoip.py`:

```python
"""IP geo-block interface (Decision 12 MVP customer-scope EU/UK exclusion).

At MVP, the DefaultIPGeoBlocker is a no-op — it returns None for every lookup
and never blocks. Real geo-block (MaxMind GeoLite2) is deferred per Decision 12
sub-deferral: ToS attestation is the load-bearing legal mechanism; geo-block
is defense-in-depth that bolts on later.

Phase 7: implement MaxMindIPGeoBlocker that loads a GeoLite2-Country.mmdb file
and resolves IP → ISO-3166 country code.
"""
from typing import Protocol


class BlockedCountryError(Exception):
    """Raised when an IP resolves to a blocked country."""

    def __init__(self, country_code: str) -> None:
        self.country_code = country_code
        super().__init__(f"signup blocked: source country {country_code} is in the exclusion list")


class IPGeoBlocker(Protocol):
    """Interface for IP → country resolution + block-list enforcement."""

    def lookup_country(self, ip: str) -> str | None:
        """Return ISO-3166 alpha-2 code for the IP, or None if unresolvable."""
        ...

    def assert_not_blocked(self, ip: str, blocked_countries: set[str]) -> None:
        """Raise BlockedCountryError if the IP resolves to a blocked country."""
        ...


class DefaultIPGeoBlocker:
    """No-op geo-blocker: never resolves, never blocks (MVP per Decision 12)."""

    def lookup_country(self, ip: str) -> str | None:
        return None

    def assert_not_blocked(self, ip: str, blocked_countries: set[str]) -> None:
        # No-op: we don't have a lookup mechanism at MVP
        return None
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/unit/test_geoip.py -v`
Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/auth/geoip.py tests/unit/test_geoip.py
git commit -m "feat(auth): IPGeoBlocker interface + DefaultIPGeoBlocker no-op (Decision 12 deferred geo-block)"
```

---

## Task 7: POST /signup endpoint (tenant + attestations + JWT)

**Files:**
- Create: `src/synthius_mem/api/signup_routes.py`
- Test: `tests/integration/test_signup.py`

- [ ] **Step 1: Write the failing test**

`tests/integration/test_signup.py`:

```python
"""POST /signup — tenant creation + scope attestation + JWT issuance."""
from fastapi import status
from fastapi.testclient import TestClient

from synthius_mem.main import app

client = TestClient(app)


def _valid_signup() -> dict:
    return {
        "subject": "alice@example.com",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True,
            "no_payment_data": True,
            "no_minors": True,
            "no_eu_uk_residents": True,
            "no_sensitive_categories": True,
        },
    }


def test_signup_with_valid_attestations_returns_jwt_and_tenant_id() -> None:
    resp = client.post("/signup", json=_valid_signup())
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "access_token" in body
    assert "tenant_id" in body
    assert body["token_type"] == "bearer"


def test_signup_with_false_attestation_rejected_422() -> None:
    body = _valid_signup()
    body["scope_attestation"]["no_phi"] = False
    resp = client.post("/signup", json=body)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_with_missing_attestation_rejected_422() -> None:
    body = _valid_signup()
    del body["scope_attestation"]["no_phi"]
    resp = client.post("/signup", json=body)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_records_tenant_and_attestation_in_db() -> None:
    """After signup, tenant + scope_attestations rows exist for the new tenant."""
    from sqlalchemy import text
    from synthius_mem.storage.db import get_engine
    from synthius_mem.storage.rls import tenant_scope

    resp = client.post("/signup", json=_valid_signup())
    assert resp.status_code == status.HTTP_200_OK
    tenant_id = resp.json()["tenant_id"]

    with get_engine().begin() as conn:
        with tenant_scope(conn, tenant_id):
            tenant_row = conn.execute(
                text("SELECT tos_version FROM tenants WHERE tenant_id = :tid"),
                {"tid": tenant_id},
            ).fetchone()
            assert tenant_row is not None
            assert tenant_row[0] == "2026-04-21-mvp"

            att_row = conn.execute(
                text("""
                    SELECT no_phi, no_payment_data, no_minors,
                           no_eu_uk_residents, no_sensitive_categories
                    FROM scope_attestations WHERE tenant_id = :tid
                """),
                {"tid": tenant_id},
            ).fetchone()
            assert att_row is not None
            assert all(att_row)  # all 5 must be True
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/integration/test_signup.py -v`
Expected: `404 Not Found` for the POST /signup endpoint (or import error for signup_routes module).

- [ ] **Step 3: Implement `signup_routes.py`**

`src/synthius_mem/api/signup_routes.py`:

```python
"""POST /signup — create a new tenant + record scope attestations + return JWT.

Per Decision 12: scope_attestation is the load-bearing legal mechanism —
all 5 fields must attest True or signup fails (422). IP geo-block is layered
on top via DefaultIPGeoBlocker (no-op at MVP).
"""
from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text

from synthius_mem.auth.geoip import (
    BlockedCountryError,
    DefaultIPGeoBlocker,
)
from synthius_mem.auth.jwt import issue_token
from synthius_mem.auth.scope_attestation import ScopeAttestation
from synthius_mem.storage.db import get_engine
from synthius_mem.storage.rls import tenant_scope

router = APIRouter()

# EU/UK ISO-3166 alpha-2 codes (Decision 12 hard exclusion)
_BLOCKED_COUNTRIES = frozenset({
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE", "GB",
})

_geo_blocker = DefaultIPGeoBlocker()


class SignupRequest(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")

    subject: str
    tos_version: str
    scope_attestation: ScopeAttestation


class SignupResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")

    access_token: str
    tenant_id: str
    token_type: str = "bearer"


@router.post("/signup")
def signup(req: SignupRequest, request: Request,
           x_forwarded_for: str | None = Header(default=None)) -> SignupResponse:
    """Create tenant + record attestations + return JWT.

    Pydantic validation already enforces:
    - All 5 ScopeAttestation fields must be True (or 422)
    - tos_version is non-empty (or 422)

    Additional checks here:
    - IP geo-block via DefaultIPGeoBlocker (no-op at MVP per Decision 12)

    Returns: SignupResponse with bearer token (8 hour TTL) + tenant_id.
    """
    source_ip = (x_forwarded_for or "").split(",")[0].strip() or (
        request.client.host if request.client else ""
    )
    source_country = _geo_blocker.lookup_country(source_ip) if source_ip else None
    # No-op at MVP; future MaxMind impl raises BlockedCountryError → map to 403.
    # Catching here makes the Phase 7 swap-in atomic — only geoip.py changes.
    try:
        _geo_blocker.assert_not_blocked(source_ip, set(_BLOCKED_COUNTRIES))
    except BlockedCountryError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail=str(e)) from e

    tenant_id = str(uuid4())

    # Write tenant + scope attestations under tenant_scope (transaction-scoped via
    # set_config(..., is_local=true) — auto-reverts on commit, so the next caller
    # of this connection from the pool does NOT inherit the tenant context).
    with get_engine().begin() as conn:
        with tenant_scope(conn, tenant_id):
            conn.execute(
                text("INSERT INTO tenants (tenant_id, tos_version) VALUES (:tid, :tos)"),
                {"tid": tenant_id, "tos": req.tos_version},
            )
            conn.execute(
                text("""
                    INSERT INTO scope_attestations
                      (tenant_id, no_phi, no_payment_data, no_minors,
                       no_eu_uk_residents, no_sensitive_categories,
                       source_ip, source_country)
                    VALUES
                      (:tid, :phi, :pay, :min, :eu, :sens, :ip, :country)
                """),
                {
                    "tid": tenant_id,
                    "phi": req.scope_attestation.no_phi,
                    "pay": req.scope_attestation.no_payment_data,
                    "min": req.scope_attestation.no_minors,
                    "eu": req.scope_attestation.no_eu_uk_residents,
                    "sens": req.scope_attestation.no_sensitive_categories,
                    "ip": source_ip or None,
                    "country": source_country,
                },
            )

    token = issue_token(
        tenant_id=tenant_id,
        subject=req.subject,
        expires_in=timedelta(hours=8),
    )
    return SignupResponse(access_token=token, tenant_id=tenant_id)
```

- [ ] **Step 4: Wire router into `main.py`**

Modify `src/synthius_mem/main.py`. Find the `app.include_router(...)` block and add:

```python
from synthius_mem.api import auth_routes, health, signup_routes

app.include_router(health.router)
app.include_router(auth_routes.router)
app.include_router(signup_routes.router)
```

- [ ] **Step 5: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_signup.py -v`
Expected: `4 passed`.

Run: `uv run pytest -q`
Expected: still all green (no regressions; new total = 49 + 4 = 53).

- [ ] **Step 6: Commit**

```bash
git add src/synthius_mem/api/signup_routes.py src/synthius_mem/main.py tests/integration/test_signup.py
git commit -m "feat(api): POST /signup — tenant + attestations + JWT (Decision 12 enforcement)"
```

---

## Task 8: POST /personas + GET /personas

**Files:**
- Create: `src/synthius_mem/api/personas.py`
- Modify: `src/synthius_mem/main.py` (remove the `/personas` stub; include personas router)
- Test: `tests/integration/test_personas.py`

- [ ] **Step 1: Write the failing test**

`tests/integration/test_personas.py`:

```python
"""POST /personas + GET /personas happy-path tests."""
from fastapi import status
from fastapi.testclient import TestClient

from synthius_mem.main import app

client = TestClient(app)


def _signup() -> str:
    """Sign up a new tenant and return the bearer token."""
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_post_personas_creates_persona_and_returns_ulid() -> None:
    token = _signup()
    resp = client.post("/personas", headers=_auth(token))
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert "persona_id" in body
    assert len(body["persona_id"]) == 26  # ULID


def test_get_personas_returns_empty_for_new_tenant() -> None:
    token = _signup()
    resp = client.get("/personas", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"personas": []}


def test_get_personas_returns_created_persona() -> None:
    token = _signup()
    create_resp = client.post("/personas", headers=_auth(token))
    persona_id = create_resp.json()["persona_id"]

    list_resp = client.get("/personas", headers=_auth(token))
    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.json() == {"personas": [persona_id]}


def test_post_personas_unauthenticated_returns_401() -> None:
    resp = client.post("/personas")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_personas_unauthenticated_returns_401() -> None:
    resp = client.get("/personas")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/integration/test_personas.py -v`
Expected: at least the 201/empty-list tests fail because the existing `/personas` stub returns `{"personas": [], "tenant_id": ...}` and only handles GET, not POST.

- [ ] **Step 3: Implement `personas.py`**

`src/synthius_mem/api/personas.py`:

```python
"""POST + GET /personas — onboard + list personas under the current tenant scope (S-1)."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.engine import Connection

from synthius_mem.auth.deps import CurrentTenant
from synthius_mem.storage.connection import request_scoped_conn
from synthius_mem.storage.repository import PersonaRepository

router = APIRouter()
_repo = PersonaRepository()


class CreatePersonaResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    persona_id: str


class ListPersonasResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    personas: list[str]


def _conn_for(claims: CurrentTenant) -> Connection:
    """Inline FastAPI dependency: yield a request-scoped Connection for the caller's tenant."""
    yield from request_scoped_conn(claims.tenant_id)


@router.post("/personas", status_code=status.HTTP_201_CREATED)
def create_persona(
    claims: CurrentTenant,
    conn: Annotated[Connection, Depends(_conn_for)],
) -> CreatePersonaResponse:
    persona_id = _repo.create_persona(conn, claims.tenant_id)
    return CreatePersonaResponse(persona_id=persona_id)


@router.get("/personas")
def list_personas(
    claims: CurrentTenant,  # noqa: ARG001 — used by Depends(_conn_for) for tenant scoping
    conn: Annotated[Connection, Depends(_conn_for)],
) -> ListPersonasResponse:
    return ListPersonasResponse(personas=_repo.list_personas(conn))
```

- [ ] **Step 4: Modify `main.py` — remove the stub + include the router**

In `src/synthius_mem/main.py`:
1. DELETE the existing `/personas` stub function (the one defined directly in `main.py` from Task 11).
2. ADD `from synthius_mem.api import personas` to the import block.
3. ADD `app.include_router(personas.router)` to the include_router block (after auth_routes).

- [ ] **Step 5: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_personas.py -v`
Expected: `5 passed`.

Run: `uv run pytest -q`
Expected: still all green; the auth_flow test from Epic 0 (which checks `/personas` is auth-protected) still passes because the new router preserves auth.

- [ ] **Step 6: Commit**

```bash
git add src/synthius_mem/api/personas.py src/synthius_mem/main.py tests/integration/test_personas.py
git commit -m "feat(api): POST /personas + GET /personas (US-1.1, US-1.2; replaces stub)"
```

---

## Task 9: Cross-tenant API isolation (LOAD-BEARING)

**Files:**
- Test: `tests/integration/test_personas_rls.py`

This task adds NO new production code — it adds a single load-bearing integration test that proves the `/personas` API correctly enforces RLS at the HTTP layer (not just the SQL layer, which Task 9 of Epic 0 covered).

- [ ] **Step 1: Write the test**

`tests/integration/test_personas_rls.py`:

```python
"""LOAD-BEARING: prove /personas API enforces cross-tenant isolation (DIR-11.1).

This is the HTTP-layer counterpart to Epic 0 Task 9's SQL-layer RLS isolation
test. If this test ever fails, do NOT ship — one bug = total cross-tenant
data breach via the API.
"""
from fastapi import status
from fastapi.testclient import TestClient

from synthius_mem.main import app

client = TestClient(app)


def _signup() -> tuple[str, str]:
    """Returns (token, tenant_id) for a new tenant."""
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    body = resp.json()
    return body["access_token"], body["tenant_id"]


def test_tenant_a_cannot_see_tenant_b_personas_via_api() -> None:
    token_a, tenant_a = _signup()
    token_b, tenant_b = _signup()
    assert tenant_a != tenant_b

    # tenant_b creates 3 personas
    created_b = []
    for _ in range(3):
        resp = client.post("/personas", headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == status.HTTP_201_CREATED
        created_b.append(resp.json()["persona_id"])

    # tenant_a lists personas — must see ZERO of tenant_b's
    resp_a = client.get("/personas", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == status.HTTP_200_OK
    visible_to_a = set(resp_a.json()["personas"])
    leaked = visible_to_a & set(created_b)
    assert leaked == set(), f"RLS BREACH at API layer: tenant_a saw tenant_b personas: {leaked}"

    # Sanity: tenant_b sees its own 3
    resp_b = client.get("/personas", headers={"Authorization": f"Bearer {token_b}"})
    assert set(resp_b.json()["personas"]) == set(created_b)
```

- [ ] **Step 2: Run test, verify PASS**

Run: `uv run pytest tests/integration/test_personas_rls.py -v`
Expected: `1 passed`.

(Why does it pass first try? Because the SQL-layer RLS from Epic 0 Task 9 does the actual work; this test just proves it composes through the API. If it FAILS, the bug is in the connection-routing or middleware — investigate before proceeding.)

- [ ] **Step 3: Run full suite**

Run: `uv run pytest -q`
Expected: all green; total now 53 + 1 = 54 (plus the Task 7-8 tests, depending on order).

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_personas_rls.py
git commit -m "test(security): cross-tenant API isolation (DIR-11.1 load-bearing) — US-1.4"
```

---

## Task 10: Refactor /auth/token to require existing tenant_id

**Files:**
- Modify: `src/synthius_mem/api/auth_routes.py`
- Modify: `tests/integration/test_auth_flow.py`

The Epic 0 `/auth/token` minted tokens for any subject with optional tenant_id (creating a new tenant if absent). With Epic 1's signup flow, that's a security hole — anyone could mint a token for a tenant they didn't sign up for. Refactor `/auth/token` to REQUIRE an existing tenant_id (no minting).

- [ ] **Step 1: Update `tests/integration/test_auth_flow.py` to add the new requirement**

Add a new test to `tests/integration/test_auth_flow.py`:

```python
def test_auth_token_requires_existing_tenant_id() -> None:
    from uuid import uuid4
    # Random tenant_id that doesn't exist in tenants table → must reject
    resp = client.post("/auth/token", json={
        "subject": "x@test",
        "tenant_id": str(uuid4()),
    })
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_auth_token_works_for_existing_tenant() -> None:
    # Sign up first to create a tenant
    signup_resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    tenant_id = signup_resp.json()["tenant_id"]

    # Now /auth/token can mint a token for that tenant
    resp = client.post("/auth/token", json={
        "subject": "u@test",
        "tenant_id": tenant_id,
    })
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["tenant_id"] == tenant_id


def test_auth_token_without_tenant_id_returns_422() -> None:
    """tenant_id is now mandatory (no anonymous minting)."""
    resp = client.post("/auth/token", json={"subject": "u@test"})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

- [ ] **Step 2: Run new tests, verify they FAIL**

Run: `uv run pytest tests/integration/test_auth_flow.py -v -k 'requires_existing or existing_tenant or without_tenant_id'`
Expected: 3 new tests FAIL (current implementation mints any tenant_id).

- [ ] **Step 3: Update `src/synthius_mem/api/auth_routes.py`**

Replace `auth_routes.py` content with:

```python
"""Auth endpoints — at MVP, simple token-mint for EXISTING tenants only.

Tenant creation is exclusively via /signup (which records scope attestations).
This endpoint cannot create tenants — only re-issue tokens for tenants that
already attested at signup. Phase 7: replace with real OAuth2 IdP.
"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text

from synthius_mem.auth.jwt import issue_token
from synthius_mem.storage.db import get_engine
from synthius_mem.storage.rls import tenant_scope

router = APIRouter()


class TokenRequest(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    subject: str
    tenant_id: str  # MANDATORY — no anonymous minting


class TokenResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    access_token: str
    tenant_id: str
    token_type: str = "bearer"


@router.post("/auth/token")
def mint_token(req: TokenRequest) -> TokenResponse:
    """Issue a token for an EXISTING tenant. Use /signup to create tenants."""
    # Verify the tenant exists (RLS-scoped read under the requested tenant_id)
    with get_engine().begin() as conn:
        with tenant_scope(conn, req.tenant_id):
            row = conn.execute(
                text("SELECT 1 FROM tenants WHERE tenant_id = :tid"),
                {"tid": req.tenant_id},
            ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found; use /signup")

    token = issue_token(
        tenant_id=req.tenant_id,
        subject=req.subject,
        expires_in=timedelta(hours=8),
    )
    return TokenResponse(access_token=token, tenant_id=req.tenant_id)
```

- [ ] **Step 4: Update existing Epic 0 tests in `test_auth_flow.py`**

The Epic 0 tests `test_unauthenticated_request_to_protected_endpoint_returns_401`, `test_valid_token_allows_access`, `test_invalid_token_returns_401` should still pass — they test the `require_auth` dependency, which is unchanged.

But `test_valid_token_allows_access` calls `issue_token(tenant_id=str(uuid4()), ...)` directly (not through `/auth/token`), so it doesn't depend on the changed endpoint.

Verify by running Epic 0 auth_flow tests:
Run: `uv run pytest tests/integration/test_auth_flow.py::test_unauthenticated_request_to_protected_endpoint_returns_401 tests/integration/test_auth_flow.py::test_valid_token_allows_access tests/integration/test_auth_flow.py::test_invalid_token_returns_401 -v`
Expected: `3 passed`.

- [ ] **Step 5: Run all auth_flow tests, verify PASS**

Run: `uv run pytest tests/integration/test_auth_flow.py -v`
Expected: `6 passed` (3 Epic 0 + 3 new from Step 1).

- [ ] **Step 6: Run full suite**

Run: `uv run pytest -q`
Expected: still all green; total now 54 + 3 = 57.

- [ ] **Step 7: Commit**

```bash
git add src/synthius_mem/api/auth_routes.py tests/integration/test_auth_flow.py
git commit -m "feat(auth): /auth/token requires existing tenant_id (no anonymous minting)"
```

---

## Epic 1 exit criteria (verify before declaring done)

Run the following and confirm:

- [ ] `uv run pytest -q` → 57 passed + 1 skipped (or close — depending on actual test counts)
- [ ] `uv run mypy src/` → clean
- [ ] `uv run ruff check .` → clean
- [ ] `POST /signup` with valid attestations creates a tenant + returns JWT (TestClient verification)
- [ ] `POST /signup` with `no_phi: false` returns 422
- [ ] `POST /personas` (with token) creates a persona (HTTP 201 + ULID)
- [ ] `GET /personas` returns ONLY the current tenant's personas (LOAD-BEARING test passes)
- [ ] `/auth/token` rejects unknown tenant_id with 404
- [ ] `/auth/token` requires tenant_id in request body (422 if missing)
- [ ] DB tables `tenants`, `personas`, `scope_attestations` exist with RLS + FORCE RLS active
- [ ] Final commit: `chore: Epic 1 (Onboard Persona) complete — exit criteria met`

---

## Notes for the executor

- **Order matters**: Tasks 1+2 (schema + migration) MUST come before any task that writes/reads new tables. Tasks 3-6 are independent (can be parallelized in subagent dispatch IF the orchestrator coordinates). Tasks 7-9 depend on 1-6. Task 10 depends on Task 7 (signup must exist before refactoring /auth/token).
- **The signup flow uses inline `set_config` in Task 7**, not `tenant_scope`, because the signup creates a NEW tenant_id that has no prior context. After signup commits, subsequent requests can use `tenant_scope` normally.
- **`request_scoped_conn` is used by the personas router via `Depends(_conn_for)` (Task 8)**. Future epics (S-2 Ingest, S-3 Recall) will use the same pattern.
- **The IPGeoBlocker no-op**: real MaxMind integration is deferred per Decision 12. The interface is in place so Phase 7 swaps the implementation without touching signup_routes.py. Document this clearly in the PR description.
- **DON'T add features not in this plan**: defer fact-related ops (S-2 ingest, S-3 query) to their respective epics.
- **Commit per task**: every task ends with a single commit.

---

## References

- **Architecture**: `docs/architecture/ARCHITECTURE.md` v1.2 §3 S-1 + Decision 12
- **Master backlog**: `docs/superpowers/plans/2026-04-21-synthius-mem-backlog.md` (Epic 1 row)
- **Prior epic plan**: `docs/superpowers/plans/2026-04-21-epic-0-foundation.md` (Foundation that this epic builds atop)
- **Skill**: `superpowers:writing-plans`
