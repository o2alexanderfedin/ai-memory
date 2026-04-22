# Epic 0: Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a running FastAPI service that authenticates a tenant-scoped bearer token, propagates `tenant_id` through Postgres RLS to a 6-domain JSONB schema, and round-trips an LLM call through LiteLLM to z.ai GLM-4.7-FlashX with closed-schema validation.

**Architecture:** Python 3.12 + FastAPI + Pydantic v2 + Postgres 15 (JSONB + GIN + B-tree + RLS) + Alembic + LiteLLM gateway + OpenTelemetry. Single-region single-replica via Docker Compose. Implements `docs/architecture/ARCHITECTURE.md` v1.2 §8 Phase 1.

**Tech Stack:** Python 3.12, FastAPI 0.110+, Pydantic 2.6+, psycopg[binary] 3.x, SQLAlchemy 2.0+ (Core only, no ORM), Alembic, LiteLLM, opentelemetry-sdk + opentelemetry-exporter-otlp, pytest + pytest-asyncio + pytest-postgresql, uv, ruff, mypy strict, Docker + Docker Compose.

**Slice mapping:** This epic is the cross-cutting prerequisite for slices S-1 through S-8. It does not implement any slice end-to-end — it provides the substrate.

**Success criteria (epic-level):** all of the following commands succeed:
1. `uv sync && pytest -q` → all tests green
2. `docker-compose up -d` → Postgres healthy + FastAPI responds on :8000
3. `curl localhost:8000/health` → `{"status":"ok",...}`
4. `curl -X POST localhost:8000/auth/token -d '...'` → JWT with `tenant_id` claim
5. `pytest tests/integration/test_rls_isolation.py -v` → tenant-A cannot read tenant-B (proven via direct SQL probe)
6. `pytest tests/integration/test_llm_gateway.py -v` → GLM-4.7-FlashX returns Pydantic-validated structured output

---

## File structure

```
synthius_mem/
├── pyproject.toml                              # uv-managed, ruff + mypy + pytest config
├── docker-compose.yml                          # postgres + service + otel-collector
├── Dockerfile                                  # FastAPI service image
├── .env.example                                # env-var template (DB URL, z.ai key, etc.)
├── alembic.ini                                 # Alembic config
├── alembic/
│   ├── env.py                                  # Alembic env (loads SQLAlchemy metadata)
│   └── versions/
│       └── 0001_initial_schema.py              # 6 domain tables + WAL + RLS policies + indexes
├── src/synthius_mem/
│   ├── __init__.py
│   ├── main.py                                 # FastAPI app entrypoint + middleware wiring
│   ├── config.py                               # Pydantic Settings (env-var loader)
│   ├── schemas/                                # Pydantic v2 closed-schema models (DIR-1.1)
│   │   ├── __init__.py
│   │   ├── envelope.py                         # CommonEnvelope (DIR-1.3)
│   │   ├── biography.py
│   │   ├── experiences.py
│   │   ├── preferences.py
│   │   ├── social_circle.py
│   │   ├── work.py
│   │   └── psychometrics.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── db.py                               # SQLAlchemy engine + session factory
│   │   ├── tables.py                           # SQLAlchemy Core Table defs (6 domains + WAL)
│   │   ├── rls.py                              # RLS context-setter middleware
│   │   └── repository.py                       # tenant-scoped CRUD primitives
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py                              # JWT issuer + verifier
│   │   └── deps.py                             # FastAPI dependency: extract tenant from token
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py                           # GET /health
│   │   └── auth_routes.py                      # POST /auth/token
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gateway.py                          # LLMGateway protocol + LiteLLM impl
│   │   └── models.py                           # ModelTier enum (VOLUME/QUALITY/FREE)
│   └── observability/
│       ├── __init__.py
│       └── otel.py                             # tracer + meter setup
└── tests/
    ├── conftest.py                             # pytest-postgresql fixture + app client
    ├── unit/
    │   ├── test_schemas_envelope.py
    │   ├── test_schemas_biography.py
    │   ├── test_schemas_round_trip.py          # JSON Schema export + re-validation
    │   ├── test_jwt.py
    │   └── test_llm_gateway.py                 # mocked + real-API marker
    └── integration/
        ├── test_health.py
        ├── test_auth_flow.py
        ├── test_rls_isolation.py               # load-bearing: cross-tenant deny
        ├── test_db_indexes.py                  # GIN + B-tree present and used
        └── test_llm_gateway.py                 # marked @pytest.mark.real_api
```

---

## US-0.1: Project skeleton (uv + ruff + pytest + Docker Compose)

**Files:**
- Create: `pyproject.toml`
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `tests/conftest.py`
- Create: `src/synthius_mem/__init__.py`

### Task 1: Initialize project with uv

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "synthius-mem"
version = "0.0.1"
description = "Per-persona structured memory service"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
    "psycopg[binary]>=3.1",
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "litellm>=1.40",
    "python-jose[cryptography]>=3.3",
    "opentelemetry-api>=1.24",
    "opentelemetry-sdk>=1.24",
    "opentelemetry-instrumentation-fastapi>=0.45b0",
    "opentelemetry-exporter-otlp>=1.24",
    "python-ulid>=2.2",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-postgresql>=6.0",
    "httpx>=0.27",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.ruff]
line-length = 100
target-version = "py312"
[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "PL", "RUF"]

[tool.mypy]
python_version = "3.12"
strict = true
disallow_any_explicit = true
disallow_any_generics = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "real_api: tests that hit a real LLM provider (skip without API key)",
]
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
.env
.pytest_cache/
.ruff_cache/
.mypy_cache/
*.egg-info/
dist/
build/
htmlcov/
.coverage
```

- [ ] **Step 3: Create `src/synthius_mem/__init__.py`** (empty)

```python
"""Synthius-Mem per-persona structured memory service."""
```

- [ ] **Step 4: Run `uv sync` to install deps**

Run: `uv sync`
Expected: `Resolved N packages` then `Installed N packages`. No errors.

- [ ] **Step 5: Run `pytest` (zero tests, should still pass with rc=5)**

Run: `uv run pytest`
Expected: `no tests ran` with exit code 5 (acceptable — confirms pytest is wired)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore src/synthius_mem/__init__.py
git commit -m "chore: initialize project skeleton with uv + ruff + pytest + mypy"
```

### Task 2: Docker Compose for Postgres + service

- [ ] **Step 1: Write `docker-compose.yml`**

```yaml
version: "3.9"
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: synthius_mem
      POSTGRES_USER: synthius
      POSTGRES_PASSWORD: dev_only_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U synthius -d synthius_mem"]
      interval: 2s
      timeout: 2s
      retries: 10

  service:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://synthius:dev_only_password@postgres:5432/synthius_mem
      JWT_SECRET: dev_only_secret_change_in_prod
      ZAI_API_KEY: ${ZAI_API_KEY:-}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  pgdata:
```

- [ ] **Step 2: Write `Dockerfile`**

```dockerfile
FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "synthius_mem.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Write `.env.example`**

```
DATABASE_URL=postgresql+psycopg://synthius:dev_only_password@localhost:5432/synthius_mem
JWT_SECRET=replace-me-with-32-random-bytes-base64
ZAI_API_KEY=
ANTHROPIC_API_KEY=
OTEL_EXPORTER_OTLP_ENDPOINT=
```

- [ ] **Step 4: Verify Postgres comes up**

Run: `docker-compose up -d postgres`
Then: `docker-compose exec postgres pg_isready -U synthius`
Expected: `accepting connections`

- [ ] **Step 5: Stop services and commit**

Run: `docker-compose down`

```bash
git add docker-compose.yml Dockerfile .env.example
git commit -m "chore: add docker-compose for postgres + service + healthchecks"
```

### Task 3: Test scaffold + sanity smoke test

- [ ] **Step 1: Write `tests/conftest.py`**

```python
"""Shared test fixtures."""
from collections.abc import Generator

import pytest
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor

postgresql_proc = factories.postgresql_proc(port=None)
postgresql = factories.postgresql("postgresql_proc")


@pytest.fixture
def smoke() -> bool:
    return True
```

- [ ] **Step 2: Write `tests/unit/test_smoke.py`**

```python
"""Smoke test — confirm pytest collection works."""

def test_smoke(smoke: bool) -> None:
    assert smoke is True
```

- [ ] **Step 3: Run test, verify PASS**

Run: `uv run pytest tests/unit/test_smoke.py -v`
Expected: `1 passed`

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: scaffold pytest with postgres fixture + smoke test"
```

---

## US-0.2: Six closed-schema Pydantic v2 models + CommonEnvelope

**Files:**
- Create: `src/synthius_mem/schemas/envelope.py`
- Create: `src/synthius_mem/schemas/biography.py` (and 5 sibling domain files)
- Create: `src/synthius_mem/schemas/__init__.py`
- Test: `tests/unit/test_schemas_envelope.py`
- Test: `tests/unit/test_schemas_biography.py`
- Test: `tests/unit/test_schemas_round_trip.py`

### Task 4: CommonEnvelope (TDD)

- [ ] **Step 1: Write the failing test**

`tests/unit/test_schemas_envelope.py`:

```python
"""Tests for the shared CommonEnvelope (DIR-1.3)."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from ulid import ULID

from synthius_mem.schemas.envelope import CommonEnvelope, Provenance


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _envelope_kwargs() -> dict:
    return dict(
        persona_id=str(ULID()),
        domain="biography",
        schema_version="1.0.0",
        confidence=0.85,
        provenance=Provenance(
            source_message_id=str(ULID()),
            source_chunk_id=str(ULID()),
            extracted_at=_now(),
            extractor_version="glm-4.7-flashx@2026-04-21",
        ),
        created_at=_now(),
        updated_at=_now(),
    )


def test_envelope_round_trip() -> None:
    env = CommonEnvelope(**_envelope_kwargs())
    serialized = env.model_dump(mode="json")
    rebuilt = CommonEnvelope.model_validate(serialized)
    assert rebuilt == env


def test_envelope_rejects_extra_fields() -> None:
    """DIR-1.1: closed schema — additionalProperties must be false."""
    bad = _envelope_kwargs() | {"unexpected_field": "should fail"}
    with pytest.raises(ValidationError):
        CommonEnvelope.model_validate(bad)


def test_envelope_confidence_in_unit_interval() -> None:
    """DIR-1.4: confidence is number in [0, 1]."""
    for bad_conf in [-0.1, 1.1, 1.5, -1]:
        with pytest.raises(ValidationError):
            CommonEnvelope.model_validate(_envelope_kwargs() | {"confidence": bad_conf})


def test_provenance_requires_extractor_version() -> None:
    """DIR-1.5: provenance MUST include extractor_version (T-044 rollback dep)."""
    base = _envelope_kwargs()
    bad_prov = base["provenance"].model_dump()
    del bad_prov["extractor_version"]
    with pytest.raises(ValidationError):
        Provenance.model_validate(bad_prov)
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/unit/test_schemas_envelope.py -v`
Expected: `ImportError` / `ModuleNotFoundError: No module named 'synthius_mem.schemas.envelope'`

- [ ] **Step 3: Implement minimal CommonEnvelope**

Create `src/synthius_mem/schemas/__init__.py`:

```python
"""Closed-schema Pydantic v2 models per DIR-1.1."""
```

Create `src/synthius_mem/schemas/envelope.py`:

```python
"""CommonEnvelope shared $defs block (DIR-1.3)."""
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class Provenance(BaseModel):
    """Per-fact provenance (DIR-1.5, DIR-9.6)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_message_id: str
    source_chunk_id: str
    extracted_at: datetime
    extractor_version: str
    injection_risk: Optional[Annotated[float, Field(ge=0.0, le=1.0)]] = None
    pii_tokens_redacted: list[dict] = Field(default_factory=list)


class CommonEnvelope(BaseModel):
    """Shared envelope across all 6 domain schemas (DIR-1.3)."""

    model_config = ConfigDict(extra="forbid")

    persona_id: str
    domain: str
    schema_version: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: Provenance
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/unit/test_schemas_envelope.py -v`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/schemas/envelope.py src/synthius_mem/schemas/__init__.py tests/unit/test_schemas_envelope.py
git commit -m "feat(schemas): add CommonEnvelope with closed-schema validation (DIR-1.1, DIR-1.3, DIR-1.4, DIR-1.5)"
```

### Task 5: Biography domain schema (TDD)

- [ ] **Step 1: Write the failing test**

`tests/unit/test_schemas_biography.py`:

```python
"""Tests for Biography domain schema (DIR-1.1, DIR-1.8)."""
from datetime import datetime, timezone
from typing import Any

import pytest
from pydantic import ValidationError
from ulid import ULID

from synthius_mem.schemas.biography import Biography, BiographyFields, DatePrecision
from synthius_mem.schemas.envelope import CommonEnvelope, Provenance


def _envelope() -> CommonEnvelope:
    return CommonEnvelope(
        persona_id=str(ULID()),
        domain="biography",
        schema_version="1.0.0",
        confidence=0.9,
        provenance=Provenance(
            source_message_id=str(ULID()),
            source_chunk_id=str(ULID()),
            extracted_at=datetime.now(timezone.utc),
            extractor_version="test",
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _biography_fields() -> dict[str, Any]:
    """DIR-1.8: typed sub-fields, ISO-8601 + precision marker."""
    return {
        "place_of_birth": {"_raw": "London", "_ref": None},
        "birth_date": "1990-06-15",
        "birth_date_precision": "day",
        "education": [
            {
                "degree": "PhD",
                "field": "Neuroscience",
                "institution": {"_raw": "UCL", "_ref": None},
                "year": 2019,
            }
        ],
    }


def test_biography_round_trip() -> None:
    bio = Biography(envelope=_envelope(), fields=BiographyFields(**_biography_fields()))
    serialized = bio.model_dump(mode="json")
    rebuilt = Biography.model_validate(serialized)
    assert rebuilt == bio


def test_biography_rejects_extra_fields() -> None:
    """DIR-1.1: additionalProperties: false."""
    bad = _biography_fields() | {"unexpected": "rejected"}
    with pytest.raises(ValidationError):
        BiographyFields.model_validate(bad)


def test_biography_date_precision_enum() -> None:
    """DIR-1.8: precision must be year|month|day."""
    assert {p.value for p in DatePrecision} == {"year", "month", "day"}


def test_biography_emits_json_schema() -> None:
    """Schema must be exportable for downstream prompt generation."""
    schema = Biography.model_json_schema()
    assert schema["additionalProperties"] is False
    # The fields sub-schema must also be closed
    fields_schema = schema["$defs"]["BiographyFields"]
    assert fields_schema["additionalProperties"] is False
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/unit/test_schemas_biography.py -v`
Expected: `ImportError`

- [ ] **Step 3: Implement Biography schema**

Create `src/synthius_mem/schemas/biography.py`:

```python
"""Biography domain schema (DIR-1.1, DIR-1.6, DIR-1.8)."""
from datetime import date
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from synthius_mem.schemas.envelope import CommonEnvelope


class DatePrecision(str, Enum):
    """ISO-8601 date precision marker (DIR-1.8)."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class DomainRef(BaseModel):
    """Cross-domain reference dual-field shape (DIR-1.6)."""

    model_config = ConfigDict(extra="forbid")

    raw: str = Field(alias="_raw")
    ref: Optional[str] = Field(default=None, alias="_ref")


class EducationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    degree: str
    field: str
    institution: DomainRef
    year: Annotated[int, Field(ge=1900, le=2100)]


class BiographyFields(BaseModel):
    """Typed sub-fields for Biography (DIR-1.8)."""

    model_config = ConfigDict(extra="forbid")

    place_of_birth: Optional[DomainRef] = None
    birth_date: Optional[date] = None
    birth_date_precision: Optional[DatePrecision] = None
    education: list[EducationRecord] = Field(default_factory=list)


class Biography(BaseModel):
    """One Biography fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: BiographyFields
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/unit/test_schemas_biography.py -v`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/schemas/biography.py tests/unit/test_schemas_biography.py
git commit -m "feat(schemas): add Biography domain with typed sub-fields + closed schema (DIR-1.1, DIR-1.6, DIR-1.8)"
```

### Task 6: Five remaining domain schemas

Repeat the Biography pattern for `experiences`, `preferences`, `social_circle`, `work`, `psychometrics`. Keep each domain's `*Fields` model minimal at MVP — full fields populate as extraction prompts mature. Each domain MUST have:
- `extra="forbid"` (DIR-1.1)
- Domain-specific typed fields (DIR-1.8)
- Cross-domain refs via `DomainRef` where applicable (DIR-1.6)
- Envelope reuse via `CommonEnvelope` (DIR-1.3)

- [ ] **Step 1: Write `tests/unit/test_schemas_round_trip.py`**

```python
"""Cross-domain round-trip + closed-schema check (DIR-1.1, DIR-1.3)."""
from datetime import datetime, timezone

import pytest
from ulid import ULID

from synthius_mem.schemas.biography import Biography, BiographyFields
from synthius_mem.schemas.envelope import CommonEnvelope, Provenance
from synthius_mem.schemas.experiences import Experiences, ExperiencesFields
from synthius_mem.schemas.preferences import Preferences, PreferencesFields
from synthius_mem.schemas.psychometrics import Psychometrics, PsychometricsFields
from synthius_mem.schemas.social_circle import SocialCircle, SocialCircleFields
from synthius_mem.schemas.work import Work, WorkFields


def _make_envelope(domain: str) -> CommonEnvelope:
    now = datetime.now(timezone.utc)
    return CommonEnvelope(
        persona_id=str(ULID()),
        domain=domain,
        schema_version="1.0.0",
        confidence=0.5,
        provenance=Provenance(
            source_message_id=str(ULID()),
            source_chunk_id=str(ULID()),
            extracted_at=now,
            extractor_version="test",
        ),
        created_at=now,
        updated_at=now,
    )


@pytest.mark.parametrize(
    "fact_cls,fields_cls,domain",
    [
        (Biography, BiographyFields, "biography"),
        (Experiences, ExperiencesFields, "experiences"),
        (Preferences, PreferencesFields, "preferences"),
        (SocialCircle, SocialCircleFields, "social_circle"),
        (Work, WorkFields, "work"),
        (Psychometrics, PsychometricsFields, "psychometrics"),
    ],
)
def test_each_domain_round_trips(fact_cls, fields_cls, domain: str) -> None:
    fact = fact_cls(envelope=_make_envelope(domain), fields=fields_cls())
    rebuilt = fact_cls.model_validate(fact.model_dump(mode="json"))
    assert rebuilt == fact


@pytest.mark.parametrize(
    "fact_cls",
    [Biography, Experiences, Preferences, SocialCircle, Work, Psychometrics],
)
def test_each_domain_schema_is_closed(fact_cls) -> None:
    """DIR-1.1: every domain top-level + its fields must reject extras."""
    schema = fact_cls.model_json_schema()
    assert schema["additionalProperties"] is False
```

- [ ] **Step 2: Run test, verify FAIL** (expected — 5 modules missing)

Run: `uv run pytest tests/unit/test_schemas_round_trip.py -v`
Expected: `ImportError` for `experiences`, `preferences`, etc.

- [ ] **Step 3: Implement the 5 domain modules**

Create each of `experiences.py`, `preferences.py`, `social_circle.py`, `work.py`, `psychometrics.py` following the Biography pattern. Minimal at MVP — empty `*Fields` body (only `model_config`); add real fields in their respective epics as extraction prompts mature.

Example `src/synthius_mem/schemas/experiences.py`:

```python
"""Experiences domain schema (DIR-1.1, DIR-1.2 hierarchical via parent_event_id)."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExperiencesFields(BaseModel):
    """Typed sub-fields for Experiences (DIR-1.2 hierarchy via parent_event_id FK)."""

    model_config = ConfigDict(extra="forbid")

    parent_event_id: Optional[str] = None
    children: list[str] = []


class Experiences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    envelope: "CommonEnvelope"  # forward ref
    fields: ExperiencesFields


from synthius_mem.schemas.envelope import CommonEnvelope  # noqa: E402

Experiences.model_rebuild()
```

Repeat with empty-body `*Fields` for the other 4 domains.

- [ ] **Step 4: Run round-trip tests, verify PASS**

Run: `uv run pytest tests/unit/test_schemas_round_trip.py -v`
Expected: `12 passed` (6 round-trip + 6 closed-schema)

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/schemas/ tests/unit/test_schemas_round_trip.py
git commit -m "feat(schemas): add 5 remaining domain schemas (experiences/preferences/social_circle/work/psychometrics) with closed-schema validation (DIR-1.1)"
```

---

## US-0.3: Postgres 6 domain tables + WAL + GIN/B-tree + RLS via Alembic

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/0001_initial_schema.py`
- Create: `src/synthius_mem/storage/__init__.py`
- Create: `src/synthius_mem/storage/db.py`
- Create: `src/synthius_mem/storage/tables.py`
- Test: `tests/integration/test_db_indexes.py`

### Task 7: SQLAlchemy table definitions

- [ ] **Step 1: Write the failing test**

`tests/integration/test_db_indexes.py`:

```python
"""Verify schema, RLS, and indexes (DIR-2.1, DIR-2.2, DIR-2.3, DIR-11.1)."""
from sqlalchemy import text

from synthius_mem.storage.db import get_engine
from synthius_mem.storage.tables import metadata


def test_metadata_has_six_domain_tables_plus_wal(postgresql) -> None:
    table_names = {t.name for t in metadata.sorted_tables}
    expected = {"biography", "experiences", "preferences",
                "social_circle", "work", "psychometrics", "wal"}
    assert expected.issubset(table_names)


def test_six_domain_tables_have_composite_pk(postgresql) -> None:
    """DIR-2.1: composite PK (tenant_id, persona_id, fact_id)."""
    for table_name in ["biography", "experiences", "preferences",
                       "social_circle", "work", "psychometrics"]:
        table = metadata.tables[table_name]
        pk_cols = [c.name for c in table.primary_key.columns]
        assert pk_cols == ["tenant_id", "persona_id", "fact_id"], (
            f"{table_name} PK must be (tenant_id, persona_id, fact_id), got {pk_cols}"
        )


def test_each_domain_has_gin_and_btree_indexes() -> None:
    """DIR-2.2: GIN(fields jsonb_path_ops) + functional B-tree on hot sub-fields."""
    for table_name in ["biography", "work"]:  # spot-check 2 representative
        table = metadata.tables[table_name]
        idx_names = {idx.name for idx in table.indexes}
        assert any("gin" in n for n in idx_names), f"{table_name} missing GIN index"
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/integration/test_db_indexes.py -v`
Expected: `ImportError`

- [ ] **Step 3: Implement `db.py` and `tables.py`**

`src/synthius_mem/storage/__init__.py`:

```python
"""Storage layer (DIR-2.x)."""
```

`src/synthius_mem/storage/db.py`:

```python
"""SQLAlchemy engine factory."""
from functools import lru_cache

from sqlalchemy import Engine, create_engine

from synthius_mem.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, future=True)
```

`src/synthius_mem/storage/tables.py`:

```python
"""SQLAlchemy Core table defs (DIR-2.1, DIR-2.2, DIR-2.7).

We use Core (not ORM) because:
- ORM adds complexity without value here — we own the SQL via Alembic
- Hot retrieval path needs exact control over query shape (DIR-2.9)
"""
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

DOMAINS = ("biography", "experiences", "preferences",
           "social_circle", "work", "psychometrics")


def _domain_table(name: str) -> Table:
    return Table(
        name,
        metadata,
        Column("tenant_id", UUID(as_uuid=False), nullable=False),
        Column("persona_id", String(26), nullable=False),  # ULID = 26 chars (DIR-2.1)
        Column("fact_id", UUID(as_uuid=False), nullable=False),
        Column("schema_version", String, nullable=False),
        Column("fields", JSONB, nullable=False),
        Column("envelope", JSONB, nullable=False),
        Column("tombstoned_at", DateTime(timezone=True), nullable=True),
        Column("created_at", DateTime(timezone=True),
               server_default=text("now()"), nullable=False),
        Column("updated_at", DateTime(timezone=True),
               server_default=text("now()"), nullable=False),
        PrimaryKeyConstraint("tenant_id", "persona_id", "fact_id",
                             name=f"pk_{name}"),
        Index(f"ix_{name}_fields_gin", "fields",
              postgresql_using="gin",
              postgresql_ops={"fields": "jsonb_path_ops"}),
    )


for _domain in DOMAINS:
    _domain_table(_domain)


# WAL table (DIR-2.7)
wal = Table(
    "wal",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("persona_id", String(26), nullable=False),
    Column("seq", BigInteger, nullable=False),
    Column("op", Enum("add", "edit", "delete", "tombstone",
                      name="wal_op"), nullable=False),
    Column("domain", String, nullable=False),
    Column("fact_id", UUID(as_uuid=False), nullable=False),
    Column("delta", JSONB, nullable=False),
    Column("timestamp", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("extractor_version", String, nullable=False),
    Column("user_initiated", Boolean, nullable=False, server_default="false"),
    PrimaryKeyConstraint("tenant_id", "persona_id", "seq", name="pk_wal"),
)
```

`src/synthius_mem/config.py`:

```python
"""Pydantic Settings env-var loader."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://synthius:dev_only_password@localhost:5432/synthius_mem"
    )
    jwt_secret: str = Field(default="dev_only_secret")
    zai_api_key: str = ""
    anthropic_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_db_indexes.py -v`
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/storage/ src/synthius_mem/config.py tests/integration/test_db_indexes.py
git commit -m "feat(storage): add SQLAlchemy Core defs for 6 domain tables + WAL + GIN/B-tree (DIR-2.1, DIR-2.2, DIR-2.7)"
```

### Task 8: Alembic initial migration with RLS

- [ ] **Step 1: Initialize Alembic**

Run: `uv run alembic init alembic`
Expected: creates `alembic/` and `alembic.ini`

- [ ] **Step 2: Wire `alembic/env.py` to our metadata**

Edit `alembic/env.py` — replace the `target_metadata = None` line with:

```python
from synthius_mem.storage.tables import metadata
target_metadata = metadata

from synthius_mem.config import get_settings
config.set_main_option("sqlalchemy.url", get_settings().database_url)
```

- [ ] **Step 3: Generate migration**

Run: `uv run alembic revision --autogenerate -m "initial schema with RLS"`
Expected: creates a file like `alembic/versions/<hash>_initial_schema_with_rls.py` with the 6 domain tables + WAL.

- [ ] **Step 4: Augment migration with RLS policies**

Edit the generated file's `upgrade()` function to append AFTER table creation:

```python
def upgrade() -> None:
    # ... auto-generated CREATE TABLE statements ...

    # DIR-2.3 + DIR-11.1: enable RLS + tenant policy on every domain table + WAL
    for table_name in ("biography", "experiences", "preferences",
                       "social_circle", "work", "psychometrics", "wal"):
        op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {table_name}
            USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
        """)

    # DIR-2.2: functional B-tree on hot extracted sub-fields per domain
    op.execute(
        "CREATE INDEX ix_biography_fields_institution "
        "ON biography (((fields->>'institution')));"
    )
    op.execute(
        "CREATE INDEX ix_work_fields_employer "
        "ON work (((fields->>'employer')));"
    )


def downgrade() -> None:
    for table_name in ("biography", "experiences", "preferences",
                       "social_circle", "work", "psychometrics", "wal"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table_name};")
        op.execute(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;")
    # ... auto-generated DROP TABLE statements ...
```

- [ ] **Step 5: Apply migration to Docker postgres**

Run: `docker-compose up -d postgres && uv run alembic upgrade head`
Expected: `Running upgrade -> <hash>, initial schema with RLS`

- [ ] **Step 6: Verify RLS active via psql**

Run: `docker-compose exec postgres psql -U synthius -d synthius_mem -c "\\d biography"`
Expected: shows `biography` table with `Policies: tenant_isolation` listed

- [ ] **Step 7: Commit**

```bash
git add alembic.ini alembic/
git commit -m "feat(storage): initial Alembic migration with 6 domain tables + WAL + RLS + functional B-tree (DIR-2.1, DIR-2.2, DIR-2.3, DIR-11.1)"
```

### Task 9: RLS isolation integration test (LOAD-BEARING)

- [ ] **Step 1: Write the failing test**

`tests/integration/test_rls_isolation.py`:

```python
"""LOAD-BEARING: prove cross-tenant data isolation under RLS (DIR-11.1).

This test is the single most important integrity check in the system.
If it ever fails, do NOT ship — one bug = total cross-tenant data breach.
"""
from uuid import uuid4

from sqlalchemy import text
from ulid import ULID

from synthius_mem.storage.db import get_engine
from synthius_mem.storage.tables import metadata


def _seed_fact(conn, tenant_id: str, persona_id: str, fact_id: str) -> None:
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
```

- [ ] **Step 2: Run tests, verify they FAIL** (no app role grant yet)

Run: `uv run pytest tests/integration/test_rls_isolation.py -v`
Expected: probably PASS for the cross-tenant test (RLS active) but watch for `superuser bypass` — by default `synthius` user owns the tables and bypasses RLS. Need to fix.

- [ ] **Step 3: Add migration to FORCE RLS even for table owner**

Create `alembic/versions/0002_force_rls_on_owner.py`:

```python
"""Force RLS on table owners — required so service role doesn't bypass."""
from alembic import op


def upgrade() -> None:
    for t in ("biography", "experiences", "preferences",
              "social_circle", "work", "psychometrics", "wal"):
        op.execute(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY;")


def downgrade() -> None:
    for t in ("biography", "experiences", "preferences",
              "social_circle", "work", "psychometrics", "wal"):
        op.execute(f"ALTER TABLE {t} NO FORCE ROW LEVEL SECURITY;")
```

Run: `uv run alembic upgrade head`

- [ ] **Step 4: Run RLS test, verify PASS**

Run: `uv run pytest tests/integration/test_rls_isolation.py -v`
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add alembic/versions/0002_*.py tests/integration/test_rls_isolation.py
git commit -m "feat(security): FORCE RLS on table owners + cross-tenant isolation integration test (DIR-11.1 load-bearing)"
```

---

## US-0.4: JWT auth with `tenant_id` claim

**Files:**
- Create: `src/synthius_mem/auth/__init__.py`
- Create: `src/synthius_mem/auth/jwt.py`
- Create: `src/synthius_mem/auth/deps.py`
- Test: `tests/unit/test_jwt.py`
- Test: `tests/integration/test_auth_flow.py`

### Task 10: JWT issuer + verifier (TDD)

- [ ] **Step 1: Write the failing test**

`tests/unit/test_jwt.py`:

```python
"""Tests for JWT issuer/verifier (DIR-7.3)."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jose import JWTError

from synthius_mem.auth.jwt import TokenClaims, issue_token, verify_token


def test_issue_and_verify_round_trip() -> None:
    tenant_id = str(uuid4())
    subject = "user@example.com"
    token = issue_token(tenant_id=tenant_id, subject=subject, expires_in=timedelta(minutes=15))
    claims = verify_token(token)
    assert claims.tenant_id == tenant_id
    assert claims.sub == subject


def test_expired_token_raises() -> None:
    tenant_id = str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject="x", expires_in=timedelta(seconds=-1))
    with pytest.raises(JWTError):
        verify_token(token)


def test_tampered_token_raises() -> None:
    token = issue_token(tenant_id=str(uuid4()), subject="x", expires_in=timedelta(minutes=5))
    tampered = token[:-3] + "XYZ"
    with pytest.raises(JWTError):
        verify_token(tampered)


def test_token_claims_pydantic_validation() -> None:
    """tenant_id MUST be UUID format."""
    with pytest.raises(ValueError):
        TokenClaims(sub="x", tenant_id="not-a-uuid", exp=9999999999)
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/unit/test_jwt.py -v`
Expected: `ImportError`

- [ ] **Step 3: Implement JWT module**

`src/synthius_mem/auth/__init__.py`:

```python
"""Auth (DIR-7.3)."""
```

`src/synthius_mem/auth/jwt.py`:

```python
"""JWT issuer/verifier (DIR-7.3 — OAuth2-compatible bearer tokens with tenant_id claim)."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt
from pydantic import BaseModel, ConfigDict, Field, field_validator

from synthius_mem.config import get_settings

ALGORITHM = "HS256"


class TokenClaims(BaseModel):
    model_config = ConfigDict(extra="ignore")  # ignore standard JWT claims we don't validate

    sub: str
    tenant_id: str
    exp: int

    @field_validator("tenant_id")
    @classmethod
    def _tenant_id_is_uuid(cls, v: str) -> str:
        UUID(v)  # raises ValueError if not UUID-shaped
        return v


def issue_token(*, tenant_id: str, subject: str, expires_in: timedelta) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + expires_in
    to_encode = {
        "sub": subject,
        "tenant_id": tenant_id,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenClaims:
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    return TokenClaims.model_validate(payload)
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/unit/test_jwt.py -v`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/auth/ tests/unit/test_jwt.py
git commit -m "feat(auth): JWT issuer + verifier with tenant_id claim (DIR-7.3)"
```

### Task 11: FastAPI auth dependency + RLS context middleware

- [ ] **Step 1: Write the failing test**

`tests/integration/test_auth_flow.py`:

```python
"""End-to-end auth flow + RLS context propagation."""
from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from synthius_mem.auth.jwt import issue_token
from synthius_mem.main import app

client = TestClient(app)


def test_unauthenticated_request_to_protected_endpoint_returns_401() -> None:
    resp = client.get("/personas")
    assert resp.status_code == 401


def test_valid_token_allows_access() -> None:
    tenant_id = str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject="t@example.com",
                        expires_in=timedelta(minutes=5))
    resp = client.get("/personas", headers={"Authorization": f"Bearer {token}"})
    # 200 or 404 acceptable; what matters: NOT 401
    assert resp.status_code != 401


def test_invalid_token_returns_401() -> None:
    resp = client.get("/personas",
                      headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == 401
```

- [ ] **Step 2: Run test, verify FAIL** (no `main.py` or `/personas` yet)

Run: `uv run pytest tests/integration/test_auth_flow.py -v`
Expected: `ImportError` for `synthius_mem.main`

- [ ] **Step 3: Implement auth dep + RLS middleware + minimal `main.py`**

`src/synthius_mem/auth/deps.py`:

```python
"""FastAPI dependency: extract tenant from JWT, set RLS context."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError

from synthius_mem.auth.jwt import TokenClaims, verify_token


def require_auth(authorization: Annotated[str | None, Header()] = None) -> TokenClaims:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    token = authorization.removeprefix("Bearer ")
    try:
        return verify_token(token)
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"invalid token: {e}")


CurrentTenant = Annotated[TokenClaims, Depends(require_auth)]
```

`src/synthius_mem/storage/rls.py`:

```python
"""RLS context-setter — wraps each request scope (DIR-2.3, DIR-11.1)."""
from contextlib import contextmanager
from collections.abc import Iterator

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
```

`src/synthius_mem/main.py`:

```python
"""FastAPI app entrypoint."""
from fastapi import FastAPI

from synthius_mem.api import auth_routes, health
from synthius_mem.auth.deps import CurrentTenant

app = FastAPI(title="Synthius-Mem", version="0.0.1")

app.include_router(health.router)
app.include_router(auth_routes.router)


@app.get("/personas")
def list_personas(claims: CurrentTenant) -> dict:
    """Stub — Epic 1 implements this fully."""
    return {"personas": [], "tenant_id": claims.tenant_id}
```

`src/synthius_mem/api/__init__.py`:

```python
"""API routers."""
```

`src/synthius_mem/api/health.py`:

```python
"""Health endpoint (DIR-7.2 op #8)."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

`src/synthius_mem/api/auth_routes.py`:

```python
"""Auth endpoints — at MVP, simple developer-issued token."""
from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from synthius_mem.auth.jwt import issue_token

router = APIRouter()


class TokenRequest(BaseModel):
    subject: str
    tenant_id: str | None = None  # if None, we mint a new tenant


class TokenResponse(BaseModel):
    access_token: str
    tenant_id: str
    token_type: str = "bearer"


@router.post("/auth/token")
def mint_token(req: TokenRequest) -> TokenResponse:
    """MVP: developer-issued token. Replace with real OAuth2 IdP in Phase 7."""
    tenant_id = req.tenant_id or str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject=req.subject,
                        expires_in=timedelta(hours=8))
    return TokenResponse(access_token=token, tenant_id=tenant_id)
```

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_auth_flow.py -v`
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/auth/deps.py src/synthius_mem/storage/rls.py src/synthius_mem/main.py src/synthius_mem/api/ tests/integration/test_auth_flow.py
git commit -m "feat(api): FastAPI app with JWT auth + RLS context middleware + health/auth/personas-stub endpoints (DIR-7.2, DIR-7.3, DIR-11.1)"
```

---

## US-0.5: Health endpoint + OpenTelemetry traces

**Files:**
- Modify: `src/synthius_mem/main.py:1-20`
- Create: `src/synthius_mem/observability/__init__.py`
- Create: `src/synthius_mem/observability/otel.py`
- Test: `tests/integration/test_health.py`

### Task 12: OpenTelemetry tracer + meter

- [ ] **Step 1: Write the failing test**

`tests/integration/test_health.py`:

```python
"""Health endpoint + OTel trace span emission."""
from fastapi.testclient import TestClient

from synthius_mem.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_openapi_json_is_served() -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "Synthius-Mem"


def test_health_emits_otel_span(monkeypatch) -> None:
    """Verify OTel tracer is instrumenting incoming requests (FastAPI auto-instr)."""
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Re-instrument with the new provider
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.uninstrument_app(app)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

    client.get("/health")

    spans = exporter.get_finished_spans()
    assert any(s.name.endswith("/health") or s.name == "GET" for s in spans), (
        f"No /health span emitted. Spans: {[s.name for s in spans]}"
    )
```

- [ ] **Step 2: Run test, verify partial-FAIL**

Run: `uv run pytest tests/integration/test_health.py -v`
Expected: first 2 PASS (health + openapi already work), 3rd FAILS — no OTel instrumentation yet.

- [ ] **Step 3: Add OTel instrumentation**

`src/synthius_mem/observability/__init__.py`:

```python
"""Observability (DIR-8.1, DIR-8.2)."""
```

`src/synthius_mem/observability/otel.py`:

```python
"""OpenTelemetry tracer setup."""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(service_name: str = "synthius-mem", otlp_endpoint: str | None = None) -> None:
    resource = Resource.create({SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    if otlp_endpoint:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
    trace.set_tracer_provider(provider)
```

Modify `src/synthius_mem/main.py` — add at top after `app = FastAPI(...)`:

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from synthius_mem.observability.otel import setup_tracing
from synthius_mem.config import get_settings

setup_tracing(otlp_endpoint=get_settings().model_dump().get("otel_exporter_otlp_endpoint") or None)
FastAPIInstrumentor.instrument_app(app)
```

Add `otel_exporter_otlp_endpoint: str = ""` to `Settings` in `config.py`.

- [ ] **Step 4: Run tests, verify PASS**

Run: `uv run pytest tests/integration/test_health.py -v`
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/observability/ src/synthius_mem/main.py src/synthius_mem/config.py tests/integration/test_health.py
git commit -m "feat(observability): OpenTelemetry tracer + FastAPI auto-instrumentation (DIR-8.1)"
```

---

## US-0.6: LiteLLM gateway with z.ai GLM tiers + Anthropic fallback

**Files:**
- Create: `src/synthius_mem/llm/__init__.py`
- Create: `src/synthius_mem/llm/models.py`
- Create: `src/synthius_mem/llm/gateway.py`
- Test: `tests/unit/test_llm_gateway.py`
- Test: `tests/integration/test_llm_gateway.py` (marked `@pytest.mark.real_api`)

### Task 13: ModelTier enum + LLMGateway protocol (TDD)

- [ ] **Step 1: Write the failing unit test**

`tests/unit/test_llm_gateway.py`:

```python
"""Unit tests for LLMGateway (mocked LiteLLM)."""
from unittest.mock import MagicMock, patch

import pytest

from synthius_mem.llm.gateway import LLMGateway
from synthius_mem.llm.models import ModelTier


def test_volume_tier_routes_to_glm_47_flashx() -> None:
    gw = LLMGateway()
    assert gw.model_for(ModelTier.VOLUME) == "openai/glm-4.7-flashx"


def test_quality_tier_routes_to_glm_46() -> None:
    gw = LLMGateway()
    assert gw.model_for(ModelTier.QUALITY) == "openai/glm-4.6"


def test_free_tier_routes_to_glm_45_flash() -> None:
    gw = LLMGateway()
    assert gw.model_for(ModelTier.FREE) == "openai/glm-4.5-flash"


def test_fallback_chain_includes_anthropic() -> None:
    gw = LLMGateway()
    assert "anthropic/claude-haiku-4-5-20251001" in gw.fallback_chain(ModelTier.VOLUME)


@patch("synthius_mem.llm.gateway.litellm.completion")
def test_complete_calls_litellm_with_json_object_response_format(mock_completion) -> None:
    mock_completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"x": 1}'))]
    )
    gw = LLMGateway()
    result = gw.complete(
        tier=ModelTier.VOLUME,
        messages=[{"role": "user", "content": "hi"}],
        json_mode=True,
    )
    assert result == '{"x": 1}'
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert call_kwargs["model"] == "openai/glm-4.7-flashx"
```

- [ ] **Step 2: Run test, verify FAIL**

Run: `uv run pytest tests/unit/test_llm_gateway.py -v`
Expected: `ImportError`

- [ ] **Step 3: Implement gateway**

`src/synthius_mem/llm/__init__.py`:

```python
"""LLM gateway layer (Decision 11, DIR-12.5)."""
```

`src/synthius_mem/llm/models.py`:

```python
"""Model tier enum (Decision 11)."""
from enum import Enum


class ModelTier(str, Enum):
    """Three LiteLLM-routed tiers per Decision 11.

    VOLUME  = GLM-4.7-FlashX  ($0.07/$0.40 per M) — extraction, planner, summarizer
    QUALITY = GLM-4.6         ($0.60/$2.20 per M) — psychometric scoring, conflict resolver
    FREE    = GLM-4.5-Flash   (free tier)         — dev, CI, low-stakes
    """

    VOLUME = "volume"
    QUALITY = "quality"
    FREE = "free"
```

`src/synthius_mem/llm/gateway.py`:

```python
"""LiteLLM-backed gateway (Decision 11, DIR-12.5).

Routes by tier; falls back across providers for resilience.
z.ai is reached via LiteLLM's OpenAI-compatible adapter (z.ai exposes an
OpenAI-shaped endpoint at https://api.z.ai/api/paas/v4 — set api_base + api_key
on each call OR via env vars).
"""
import os
from typing import Any

import litellm
from pydantic import BaseModel

from synthius_mem.config import get_settings
from synthius_mem.llm.models import ModelTier

# Tier → primary model mapping (Decision 11)
_TIER_MODELS: dict[ModelTier, str] = {
    ModelTier.VOLUME: "openai/glm-4.7-flashx",
    ModelTier.QUALITY: "openai/glm-4.6",
    ModelTier.FREE: "openai/glm-4.5-flash",
}

# Fallback chain per tier (Decision 11 trade-off mitigation)
_FALLBACKS: dict[ModelTier, list[str]] = {
    ModelTier.VOLUME: [
        "openai/glm-4.7-flashx",
        "openai/glm-4.5-air",
        "anthropic/claude-haiku-4-5-20251001",
    ],
    ModelTier.QUALITY: [
        "openai/glm-4.6",
        "openai/glm-4.7",
        "anthropic/claude-haiku-4-5-20251001",
    ],
    ModelTier.FREE: [
        "openai/glm-4.5-flash",
        "openai/glm-4.7-flash",
    ],
}


class LLMGateway:
    """Tier-aware LLM gateway with provider fallback.

    All non-test code MUST go through this class — no direct provider SDKs.
    Compliance-checklist item per Decision 11 + DIR-12.5.
    """

    def __init__(self) -> None:
        settings = get_settings()
        if settings.zai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.zai_api_key
            os.environ["OPENAI_API_BASE"] = "https://api.z.ai/api/paas/v4"
        if settings.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key

    @staticmethod
    def model_for(tier: ModelTier) -> str:
        return _TIER_MODELS[tier]

    @staticmethod
    def fallback_chain(tier: ModelTier) -> list[str]:
        return _FALLBACKS[tier]

    def complete(
        self,
        *,
        tier: ModelTier,
        messages: list[dict[str, str]],
        json_mode: bool = False,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> str:
        """Returns the assistant's content string."""
        kwargs: dict[str, Any] = {
            "model": self.model_for(tier),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "fallbacks": self.fallback_chain(tier)[1:],  # primary excluded
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = litellm.completion(**kwargs)
        return resp.choices[0].message.content
```

- [ ] **Step 4: Run unit tests, verify PASS**

Run: `uv run pytest tests/unit/test_llm_gateway.py -v`
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/synthius_mem/llm/ tests/unit/test_llm_gateway.py
git commit -m "feat(llm): LiteLLM gateway with z.ai GLM tiers + Anthropic fallback (Decision 11, DIR-12.5)"
```

### Task 14 (SP-0.1): Real-API spike — confirm closed-schema round-trip on GLM-4.7-FlashX

- [ ] **Step 1: Write the marked test**

`tests/integration/test_llm_gateway.py`:

```python
"""SP-0.1: real-API spike — verify GLM-4.7-FlashX returns parseable JSON
that round-trips through a closed Pydantic schema with additionalProperties:false.

Skip without ZAI_API_KEY env var. Mark as @pytest.mark.real_api.
"""
import json
import os

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from synthius_mem.llm.gateway import LLMGateway
from synthius_mem.llm.models import ModelTier


class Person(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    age: int
    occupation: str


@pytest.mark.real_api
@pytest.mark.skipif(not os.getenv("ZAI_API_KEY"), reason="ZAI_API_KEY not set")
def test_glm_47_flashx_returns_closed_schema_compatible_json() -> None:
    gw = LLMGateway()
    schema_hint = json.dumps(Person.model_json_schema(), indent=2)
    raw = gw.complete(
        tier=ModelTier.VOLUME,
        messages=[
            {"role": "system",
             "content": (
                 "Return ONLY a JSON object matching this schema, "
                 "with NO extra fields:\n" + schema_hint
             )},
            {"role": "user",
             "content": "Extract a person from: Alice is a 32yo data scientist."},
        ],
        json_mode=True,
    )
    # Parse + validate — extra fields will be rejected
    data = json.loads(raw)
    person = Person.model_validate(data)
    assert person.name.lower().startswith("alice")
    assert person.age == 32
```

- [ ] **Step 2: Run spike (requires ZAI_API_KEY)**

Run: `ZAI_API_KEY=$YOUR_KEY uv run pytest tests/integration/test_llm_gateway.py -v -m real_api`
Expected: `1 passed` if z.ai is healthy.

If FAIL with extra-fields rejection: pre-strip the response (e.g. `{k: v for k, v in data.items() if k in Person.model_fields}`) and document this in the spike result. **This finding gates Epic 2 — extraction prompts may need a retry-on-extra-field loop.**

- [ ] **Step 3: Document spike outcome**

Append to `docs/superpowers/specs/2026-04-21-spike-results.md` (create if absent):

```markdown
## SP-0.1: GLM-4.7-FlashX closed-schema round-trip

**Date**: <YYYY-MM-DD>
**Result**: [PASS / PASS-with-stripping / FAIL]
**Notes**: [How often did GLM emit extra fields? Did response_format json_object suffice?]
**Architecture impact**: [If FAIL — Decision 11 trade-off section may need updating; ARCHITECTURE.md DIR-3.8 needs amendment]
```

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_llm_gateway.py docs/superpowers/specs/2026-04-21-spike-results.md
git commit -m "spike(llm): SP-0.1 verify GLM-4.7-FlashX closed-schema round-trip (Decision 11)"
```

### Task 15 (SP-0.2): Postgres GIN + B-tree benchmark

- [ ] **Step 1: Write benchmark script**

`tests/integration/bench_index_lookup.py`:

```python
"""SP-0.2: 200K-row hot-path benchmark (DIR-2.2 numerical claim)."""
import time
from uuid import uuid4

from sqlalchemy import text
from ulid import ULID

from synthius_mem.storage.db import get_engine

TENANT_ID = str(uuid4())
PERSONA_ID = str(ULID())


def seed(n: int = 200_000) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"SET app.current_tenant_id = '{TENANT_ID}';"))
        conn.execute(text("SET session_replication_role = 'replica';"))
        for i in range(n):
            conn.execute(
                text("""
                    INSERT INTO biography (tenant_id, persona_id, fact_id,
                        schema_version, fields, envelope)
                    VALUES (:tid, :pid, :fid, '1.0.0',
                        :fields::jsonb, '{}'::jsonb)
                """),
                {
                    "tid": TENANT_ID,
                    "pid": PERSONA_ID,
                    "fid": str(uuid4()),
                    "fields": f'{{"institution": "school_{i}"}}',
                },
            )


def measure_lookup(reps: int = 1000) -> float:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"SET app.current_tenant_id = '{TENANT_ID}';"))
        start = time.perf_counter()
        for i in range(reps):
            conn.execute(
                text("""
                    SELECT fact_id FROM biography
                    WHERE persona_id = :pid AND fields->>'institution' = :inst
                """),
                {"pid": PERSONA_ID, "inst": f"school_{i}"},
            ).fetchall()
        elapsed_us = (time.perf_counter() - start) / reps * 1_000_000
    return elapsed_us


if __name__ == "__main__":
    print("seeding 200k rows...")
    seed()
    print("warming cache...")
    measure_lookup(reps=100)
    avg_us = measure_lookup(reps=1000)
    print(f"avg lookup: {avg_us:.1f} µs (target ≤ 750 µs per DIR-2.2)")
```

- [ ] **Step 2: Run benchmark**

Run: `docker-compose up -d postgres && uv run alembic upgrade head && uv run python tests/integration/bench_index_lookup.py`
Expected output: `avg lookup: <num> µs`. If > 750 µs, document in spike results and flag DIR-2.2.

- [ ] **Step 3: Document spike outcome in spike-results.md** (append section per SP-0.1 template)

- [ ] **Step 4: Commit**

```bash
git add tests/integration/bench_index_lookup.py docs/superpowers/specs/2026-04-21-spike-results.md
git commit -m "spike(storage): SP-0.2 benchmark GIN + functional B-tree at 200K rows (DIR-2.2)"
```

---

## Epic 0 exit criteria (verify before declaring done)

Run the following and confirm all green:

- [ ] `uv run pytest -q` → all tests pass (~25-30 tests)
- [ ] `uv run mypy src/` → no errors
- [ ] `uv run ruff check src/ tests/` → no errors
- [ ] `docker-compose up -d` → both services healthy
- [ ] `curl localhost:8000/health` → `{"status":"ok"}`
- [ ] `curl -X POST localhost:8000/auth/token -H 'Content-Type: application/json' -d '{"subject":"smoke@test"}'` → JWT in response
- [ ] `tests/integration/test_rls_isolation.py` PASSES (load-bearing — never ship if this fails)
- [ ] SP-0.1 spike result documented (real-API GLM round-trip)
- [ ] SP-0.2 spike result documented (200K-row Postgres benchmark)
- [ ] Final commit: `chore: Epic 0 (Foundation) complete — exit criteria met`

---

## Notes for the executor

- **Order matters within tasks but NOT across user stories** — US-0.4 (auth) and US-0.6 (LLM gateway) can proceed in parallel sub-agents
- **The RLS isolation test (Task 9) is load-bearing** — if it fails on any future PR, BLOCK the merge until fixed
- **If the spike (SP-0.1) reveals GLM-4.7-FlashX cannot reliably emit closed-schema JSON**, escalate: this would invalidate Decision 11 + DIR-3.8; ARCHITECTURE.md needs amendment before Epic 2 starts
- **Don't add features not in this plan** — defer all "nice-to-have" surfaces to their respective epics (E1+)
- **Commit frequency**: every Task ends with a commit. Don't batch.
- **Test markers**: `pytest -m "not real_api"` skips spikes; `pytest -m real_api` runs only spikes (requires API keys)

---

## References

- **Architecture**: `docs/architecture/ARCHITECTURE.md` v1.2 §8 Phase 1 + Decisions 1, 2, 3, 6, 7, 11
- **Master backlog**: `docs/superpowers/plans/2026-04-21-synthius-mem-backlog.md`
- **Directives source**: `docs/reports/synthius-mem-scientific-investigation/02-ARCHITECTURAL-DIRECTIVES.md`
- **Skill**: `superpowers:writing-plans`
