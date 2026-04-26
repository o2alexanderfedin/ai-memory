# Note — `ai-memory-host` (this repo, survey subject 09)

**Status:** active (working tree, branch `main`).
**Working dir:** `/Users/alexanderfedin/Projects/ai-memory/` — do NOT clone.

## What it is

`ai-hive-memory` (codename Synthius-Mem) — a Python 3.12 FastAPI service that
persists per-persona facts into six closed-schema Postgres tables
(`biography`, `experiences`, `preferences`, `social_circle`, `work`,
`psychometrics`) under Postgres RLS multi-tenancy. Architecturally
**embedding-free**: retrieval is exact typed-field match over JSONB indexed
by GIN + functional B-tree. LLM use is via LiteLLM (default tier: z.ai GLM;
Anthropic Haiku is only a fallback model id).

## Survey-relevant facts

- **No Claude Code integration today.** No `CLAUDE.md` at root, no MCP
  server in `src/`, no slash-command surface. `MCP` appears only as a
  future deployment variant in `docs/architecture/ARCHITECTURE.md`
  (DIR-7.5 / Decision 8).
- Sits **orthogonal** to Simon Scrapes' 6-level video taxonomy; recorded
  as `video_level = n/a` in DIMENSIONS.
- Maturity: `experimental` (version 0.0.1; Epic 1 merged, Epic 2 in flight).
- License: undeclared in repo metadata (no `LICENSE` file, no `license`
  key in `pyproject.toml`).

## Files worth re-reading

- `docs/architecture/ARCHITECTURE.md` — design intent, decisions, slices.
- `src/ai_hive_memory/storage/{tables,rls,repository}.py` — RLS posture.
- `src/ai_hive_memory/schemas/*.py` — typed-schema shape.
- `src/ai_hive_memory/llm/gateway.py` — LiteLLM tiering and fallback chain.

Findings file: `notes/cc-memory-systems-survey/findings/09-ai-memory-host.md`.
