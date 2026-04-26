# Brief 09 — `ai-memory` (this repo)

- **Name:** ai-hive-memory (the repo hosting this survey)
- **Slug:** `ai-memory-host`
- **Video level:** n/a (not pitched against the video taxonomy — describe where it sits)
- **Source URLs / paths:**
  - On disk: `/Users/alexanderfedin/Projects/ai-memory/`
  - `pyproject.toml`, `src/ai_hive_memory/`, `docs/architecture/ARCHITECTURE.md`
  - Existing milestone reports under `docs/reports/` (e.g., `synthius-mem-scientific-investigation/`)

## Cloning guidance

**No.** Already on disk at `/Users/alexanderfedin/Projects/ai-memory/`. Do **not** clone or copy.

## Anchors (so you don't start from scratch)

- Package layout: `src/ai_hive_memory/` with `api/`, `auth/`, `ingest/`, `llm/`, `observability/`, `schemas/`, `storage/`.
- Storage: Postgres (psycopg + SQLAlchemy + Alembic), with row-level security (`storage/rls.py`) and a tenant/persona model (`api/personas.py`, `api/auth_routes.py`).
- Schemas (typed-schema, not free-form markdown): `biography.py`, `experiences.py`, `preferences.py`, `psychometrics.py`, `social_circle.py`, `work.py` — i.e., per-persona structured memory.
- Ingest pipeline: `ingest/messages.py` + `ingest/adapters/` (LiteLLM-based — see `pyproject.toml`).
- Observability: OpenTelemetry instrumentation (`observability/`).
- API surface: FastAPI (`main.py`, `api/*.py`).
- Recent direction: Epic 1 "Onboard Persona" merged (see git log). `/auth/token` requires existing tenant_id.

## Investigation steps

1. Read `docs/architecture/ARCHITECTURE.md` end-to-end. Capture the design intent in one paragraph.
2. Skim `src/ai_hive_memory/schemas/*.py` to characterize the typed-memory shape (what fields exist for each persona dimension).
3. Skim `src/ai_hive_memory/storage/{repository,rls,tables}.py` for the persistence + multi-tenancy model.
4. Skim `src/ai_hive_memory/api/*.py` for the API contract — this defines integration story (D1/D3 in DIMENSIONS).
5. Look for Claude Code integration: search for `MCP`, `CLAUDE.md`, `claude-code` in repo. If absent, record as `none` honestly.
6. Capture license from `pyproject.toml` / LICENSE file.
7. Record the **honest** comparison: where does this repo sit on Simon Scrapes' 6-level scale, if anywhere? It may be orthogonal — a typed persona-memory backend rather than a Claude Code memory layer. Say so.

## Output

- **Findings:** `findings/09-ai-memory-host.md` — DIMENSIONS table + ≤ 800 words.
- **Notes:** `3rd-party/notes/ai-memory-host.md` — ≤ 200 words.
- **Format:** see DIMENSIONS.md.
- **Tone:** neutral. Do not advocate for the host repo. The synthesizer will compare; you describe.

## INDEX.md row to add

```
| ai-memory (host) | (this repo — no clone) | n/a (working tree) | Claude Code Memory Systems Survey | self | 2026-04-25 | Survey subject 09 — typed persona-memory backend |
```
