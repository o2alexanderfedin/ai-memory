# Findings 09 — `ai-hive-memory` (host repo, slug `ai-memory-host`)

**Researcher:** #09
**Date:** 2026-04-25
**Working tree commit:** `n/a (working tree)` — described against branch `main` at `1e26c88` (latest at survey time).
**Tone:** strictly descriptive. The host repo is also the survey commissioner; this entry describes only what the working tree currently implements, not what the architecture document aspires to.

## Dimension table

| #  | Dimension | Value |
|----|-----------|-------|
| A1 | `name` | `ai-hive-memory` (codename "Synthius-Mem" in `ARCHITECTURE.md`) |
| A2 | `vendor_or_author` | `o2alexanderfedin` (single-author git history); package metadata sets project name only |
| A3 | `license` | `unknown` (no `LICENSE` file at repo root; `pyproject.toml` declares no `license` key) |
| A4 | `source_availability` | `public-repo` (open working tree on disk; private/public on remote not asserted here) |
| A5 | `video_level` | `n/a` (orthogonal to Simon Scrapes' Claude-Code-memory taxonomy — see prose) |
| A6 | `maturity` | `experimental` (version `0.0.1`; Epic 1 "Onboard Persona" merged, Epic 2 "Ingest" mid-flight per git log) |
| B1 | `storage_backend` | `postgres` (Postgres JSONB + GIN + functional B-tree per `storage/tables.py`, DIR-2.1/2.2) |
| B2 | `retrieval_mechanism` | `structured-query` (exact equality / range / `in` over typed fields; explicitly embedding-free per Decision 1 / T-034) |
| B3 | `write_path` | `auto-extracted` (planned: 6 parallel LLM extractors fan-out per ingest job; see `ingest/` and Slice S-2 in `ARCHITECTURE.md`) |
| B4 | `update_model` | `versioned` (per-persona WAL append-only + materialized snapshot, DIR-2.7) |
| B5 | `memory_unit` | `record` (one fact per row in one of 6 domain tables, each `{tenant_id, persona_id, fact_id, schema_version, fields jsonb, envelope jsonb}`) |
| B6 | `schema_shape` | `typed-schema` (6 closed Pydantic schemas — `biography`, `experiences`, `preferences`, `psychometrics`, `social_circle`, `work` — each with `extra="forbid"` and a shared `CommonEnvelope`) |
| C1 | `write_latency` | `unknown` (no measured number; arch target is "preserves 21.79 ms read path") |
| C2 | `read_latency` | `21.79 ms@arch-target-mean` (claimed in `ARCHITECTURE.md` §1.1; **self-measured number not yet published in repo**; warm-cache budget breakdown estimates ~750 µs probe) |
| C3 | `recall_accuracy` | `unknown` (no benchmark run committed; references LoCoMo as a future target) |
| C4 | `scale_ceiling` | `200K rows@arch-budget` (architecture sizes hot path against 200K rows on warm cache; no production data) |
| C5 | `token_overhead_per_turn` | `unknown` (DIR-5.5 specifies a `2000/k` per-domain quota; no measured per-turn number) |
| C6 | `cost_model` | self-host (Postgres + LiteLLM-routed LLM calls; default GLM tier, Anthropic Haiku as fallback) |
| D1 | `cc_integration` | `none` (no `CLAUDE.md`, no MCP server code, no Claude-Code-specific surface in `src/`. `MCP` appears only as a **future deployment topology** in `ARCHITECTURE.md` §DIR-7.5 / Decision 8. Anthropic Haiku appears only as an LLM **fallback model** in `llm/gateway.py`, not an integration with Claude Code as a client.) |
| D2 | `other_clients` | `none` today. Architecture lists "REST + gRPC + OpenAPI 3.1, optionally also as MCP server" as the contract surface; only REST is wired up so far (FastAPI, 5 routers). |
| D3 | `protocols` | `REST` (FastAPI app in `main.py` mounts `/personas`, `/auth/token`, `/signup`, `/health`, `/`; no gRPC, no MCP server in code) |
| D4 | `lock_in_level` | `low` (data is plain Postgres rows + JSONB; schemas are Pydantic; no proprietary format) |
| D5 | `composability` | `standalone` (designed as an external memory service a host agent calls; no claimed coupling to other survey entries) |
| E1 | `setup_complexity` | `4` (multi-service: Postgres + the FastAPI service + an LLM provider; `docker-compose.yml` and Alembic migrations included) |
| E2 | `maintenance_burden` | `medium` (Postgres ops + Alembic migrations + LLM provider keys; OTel collector optional) |
| E3 | `observability` | `traces` (OpenTelemetry tracer in `observability/otel.py`; FastAPI auto-instrumentation in `main.py`. Metrics/dashboards listed as 12 SLIs in `ARCHITECTURE.md` §8 are not yet wired.) |
| E4 | `failure_modes` | LLM-extraction outages cascade into ingest DLQ; RLS misconfiguration would cross-tenant leak (single load-bearing guard per DIR-11.1). |
| E5 | `data_locality` | `self-host` (operator runs the Postgres and the FastAPI service; LLM calls go to whichever provider the operator configures via LiteLLM) |
| E6 | `privacy_posture` | Multi-tenant by composite PK `(tenant_id, persona_id)` enforced via Postgres RLS (`storage/rls.py` sets `app.current_tenant_id` per transaction). Architecture specifies per-persona DEK + KMS crypto-shred for erasure (DIR-10.2/11.2); not yet implemented in `src/`. |
| F1 | `best_fit` | A typed, per-persona structured-memory backend for a host agent that wants exact-field recall (biography, work, preferences, social circle, experiences, psychometrics) without managing a vector DB. |
| F2 | `anti_patterns` | Free-form note-taking, semantic recall over unstructured prose, single-user local memory — embedding-free design is by construction not the right tool for similarity search. |
| F3 | `not_for` | Claude-Code-specific scratchpad workflows (no integration today); workloads requiring streaming ingest (explicitly deferred, DIR-12.6); regulated workloads needing PHI/PCI/EU-resident scope (Decision 12 excludes these pre-revenue). |
| F4 | `evidence_links` | – `/Users/alexanderfedin/Projects/ai-memory/pyproject.toml` <br>– `/Users/alexanderfedin/Projects/ai-memory/docs/architecture/ARCHITECTURE.md` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/main.py` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/storage/{tables,rls,repository}.py` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/schemas/{envelope,biography,experiences,preferences,psychometrics,social_circle,work}.py` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/api/{personas,auth_routes,signup_routes,health,index}.py` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/ingest/{messages,idempotency,pii,chunker}.py` and `ingest/adapters/*` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/llm/gateway.py` <br>– `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/observability/otel.py` |
| G1 | `relation_to_host_repo` | This **is** the host repo. The survey was commissioned to compare external Claude-Code memory systems against the design space this project occupies. |
| G2 | `open_questions` | License is undeclared in repo metadata; whether the project intends to ship as OSS, source-available, or proprietary is not asserted in tracked files. The 21.79 ms claim in `ARCHITECTURE.md` is a target inherited from the source paper — no in-repo benchmark file substantiates it yet. The MCP-server variant (DIR-7.5) has no code skeleton in `src/`. |

---

## Long-form description (≤ 800 words)

### What the repo actually is

`ai-hive-memory` (codename Synthius-Mem in the architecture document) is a **per-persona structured memory backend service**. It is a Python 3.12 FastAPI application that persists facts about a "persona" into one of six closed-schema Postgres tables (`biography`, `experiences`, `preferences`, `social_circle`, `work`, `psychometrics`), and is intended to serve those facts to a host agent's "Answer LLM" as typed evidence. The headline architectural commitment is that retrieval is **embedding-free** — strict typed-field equality / range / `in` queries against JSONB columns indexed by GIN and functional B-trees, sized for a 21.79 ms mean retrieval target on 200K rows warm.

The unit of memory is a **record** (one row per fact, keyed by `(tenant_id, persona_id, fact_id)`), not a chunk or a turn. Every fact carries a `CommonEnvelope` (`schemas/envelope.py`) with `confidence`, `provenance`, `schema_version`, and timestamps; every domain schema is a Pydantic model with `model_config = ConfigDict(extra="forbid")`. This is `typed-schema` in the DIMENSIONS sense, not `semi-structured`.

### Current implementation status (working tree)

The working tree is meaningfully ahead of "skeleton" but well behind "feature complete":

- **Storage and tenancy:** `storage/tables.py` defines the 6 domain tables, `wal`, `personas`, `tenants`, plus ingest tables (`ingest_jobs`, `pending_facts`). Multi-tenancy is enforced via Postgres RLS — `storage/rls.py` sets `app.current_tenant_id` per transaction with `set_config(..., is_local=true)`. The `PersonaRepository` is intentionally stateless and trusts RLS to do cross-tenant deny.
- **API:** `main.py` mounts five routers (`/`, `/health`, `/auth/token`, `/signup`, `/personas`). `/auth/token` mints a JWT only for an existing tenant_id (per the most recent merge, `767befd`). Persona create/list (Slice S-1, "Onboard Persona") is implemented and Epic 1 closed (`85738bd`). Slices S-2 through S-8 are not yet exposed as endpoints.
- **Ingest:** `ingest/` has a canonical `Message` model with a `canonical_signature()` for SHA-256 idempotency, an `AdapterRouter` Protocol, and five source adapters (`whatsapp`, `telegram`, `pdf`, `email_mime`, `voice`). PII scrubbing is a regex `LitePIIScrubber` (Presidio is deferred per Decision 12). Extraction fan-out, consolidation, retrieval, and psychometric scoring are not yet implemented.
- **LLM gateway:** `llm/gateway.py` wraps LiteLLM with three tiers (`VOLUME`, `QUALITY`, `FREE`) and a fallback chain. Defaults are z.ai GLM models; Anthropic Haiku is a fallback model only.
- **Observability:** `observability/otel.py` configures the OpenTelemetry tracer; `main.py` calls `FastAPIInstrumentor.instrument_app`. Metrics, dashboards, and the 12 SLIs described in `ARCHITECTURE.md` §8 are not in the source tree.

### Why `cc_integration = none` and `video_level = n/a`

I searched the repo (excluding `3rd-party/` and `.venv/`) for `claude`, `claude-code`, `MCP`, and `CLAUDE.md`. The findings:

- The only `CLAUDE.md` in the tree sits inside `docs/reports/synthius-mem-scientific-investigation/ledger/hupyy-cpp-to-rust/` — that is an unrelated investigation subject, not a host-repo Claude-Code instruction file.
- "MCP" appears only as a **future deployment variant** in `ARCHITECTURE.md` (DIR-7.5, Decision 8: "MCP-server-only kept as compatible-sibling for MCP-native hosts"). No MCP server code exists in `src/`.
- "claude" appears in `src/` only as the model id `anthropic/claude-haiku-4-5-20251001` in the LLM gateway's fallback chain — i.e., the service can call Claude as one of several upstream LLM providers. That is the inverse of integrating with Claude Code as a memory layer.

The Simon Scrapes 6-level video taxonomy ranks Claude-Code memory practices on a continuum from `CLAUDE.md` files through MCP servers. This repo sits orthogonal to that axis: it is a backend service in the same problem domain as the survey's other subjects, but it does not currently expose any Claude-Code-specific surface. Recording `video_level = n/a` and `cc_integration = none` is the honest description, not a downgrade.

### Surprises / where the brief's anchors held or didn't

- **Held:** typed-schema, RLS multi-tenancy, OpenTelemetry, FastAPI, LiteLLM, six domain schemas — all present as the brief described.
- **Surprise:** Presidio is *not* yet wired in (regex `LitePIIScrubber` shipped first, Presidio deferred per Decision 12).
- **Surprise:** There is no `LICENSE` file at the repo root and `pyproject.toml` declares no license metadata, so A3 is `unknown` rather than a specific SPDX identifier.

### Count of `unknown` cells

5 cells: A3 (`license`), C1 (`write_latency`), C3 (`recall_accuracy`), C5 (`token_overhead_per_turn`), and the partially-unknown C2 (`read_latency` is an architectural target, not a measured number).
