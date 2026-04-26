# DIMENSIONS — Apples-to-Apples Schema

Every researcher fills in **all** of the fields below for their subject. If a
value is not publicly documented, write `unknown` — never guess. Findings are
written in `findings/<NN>-<slug>.md`. The synthesizer will lift these straight
into a comparison matrix, so column names and value formats must match.

> Format hint: present these as a leading table at the top of each findings
> file (one row per dimension). Long-form discussion goes below the table.

## Group A — Identity

| # | Dimension | What to record | Format |
|---|---|---|---|
| A1 | `name` | Canonical name of the system | string |
| A2 | `vendor_or_author` | Organization or individuals behind it | string |
| A3 | `license` | OSS license or "proprietary SaaS" | SPDX id / `proprietary` / `unknown` |
| A4 | `source_availability` | Where source/docs live | `public-repo` / `docs-only` / `closed` / `mixed` |
| A5 | `video_level` | Level in Simon Scrapes' 6-level taxonomy | `1`–`6` / `n/a` |
| A6 | `maturity` | Project age + activity signal | `experimental` / `active` / `stable` / `dormant` / `unknown` |

## Group B — Architecture

| # | Dimension | What to record | Format |
|---|---|---|---|
| B1 | `storage_backend` | Where memories physically live | `markdown-files` / `sqlite` / `postgres` / `vector-db:<name>` / `graph-db:<name>` / `cloud-saas` / `hybrid:<...>` |
| B2 | `retrieval_mechanism` | How memories are recalled | `keyword` / `semantic` / `structured-query` / `agentic-search` / `hybrid:<...>` |
| B3 | `write_path` | How memories are created | `manual` / `auto-extracted` / `agentic` / `hybrid` |
| B4 | `update_model` | How existing memories evolve | `append-only` / `overwrite` / `merge` / `versioned` / `n/a` |
| B5 | `memory_unit` | What is stored at a time | `file` / `chunk` / `triple` / `record` / `conversation-turn` / `other:<...>` |
| B6 | `schema_shape` | Free-form vs. structured | `unstructured` / `semi-structured` / `typed-schema` |

## Group C — Performance

(All numeric values: cite the source — benchmark, blog post, README claim.
If self-measured during this survey, mark `self-measured`.)

| # | Dimension | What to record | Format |
|---|---|---|---|
| C1 | `write_latency` | Time to persist one memory | ms / `unknown` |
| C2 | `read_latency` | Time to retrieve top-k | ms / `unknown` |
| C3 | `recall_accuracy` | If benchmarked (e.g., LoCoMo, MemBench) | `<score>@<benchmark>` / `unknown` |
| C4 | `scale_ceiling` | Documented limit (records, tokens, GB) | string / `unknown` |
| C5 | `token_overhead_per_turn` | Extra context tokens injected per turn | tokens / `unknown` |
| C6 | `cost_model` | Pricing or self-host cost driver | string |

## Group D — Integration

| # | Dimension | What to record | Format |
|---|---|---|---|
| D1 | `cc_integration` | How it plugs into Claude Code | `native` / `CLAUDE.md` / `slash-command` / `hook` / `MCP-server` / `external-CLI` / `none` |
| D2 | `other_clients` | Tools beyond Claude Code | comma-list (e.g., `cursor, windsurf, openai-sdk`) / `none` |
| D3 | `protocols` | Standards exposed | `MCP` / `OpenAI-tools` / `REST` / `gRPC` / `proprietary-API` / `none` |
| D4 | `lock_in_level` | How hard to migrate off | `low` / `medium` / `high` |
| D5 | `composability` | Can it run alongside other entries in this survey | `composes-with:<...>` / `competes-with:<...>` / `supersedes:<...>` / `standalone` |

## Group E — Operational

| # | Dimension | What to record | Format |
|---|---|---|---|
| E1 | `setup_complexity` | Effort to first useful state | `1` (drop-in) – `5` (multi-service deploy) |
| E2 | `maintenance_burden` | Ongoing care | `none` / `low` / `medium` / `high` |
| E3 | `observability` | What you can see when it misbehaves | `none` / `logs` / `metrics` / `traces` / `ui-dashboard` / `mixed` |
| E4 | `failure_modes` | Known/likely ways it breaks | short prose (≤ 2 sentences) |
| E5 | `data_locality` | Where the data physically sits | `local-only` / `self-host` / `vendor-cloud` / `mixed` |
| E6 | `privacy_posture` | PII / encryption / multi-tenant story | short prose (≤ 2 sentences) |

## Group F — Applicability

| # | Dimension | What to record | Format |
|---|---|---|---|
| F1 | `best_fit` | One sentence: ideal use case | prose |
| F2 | `anti_patterns` | When to avoid it | prose |
| F3 | `not_for` | Workloads it explicitly does not target | prose |
| F4 | `evidence_links` | URLs/files that back the above | bulleted list |

## Group G — Survey-specific notes

| # | Dimension | What to record | Format |
|---|---|---|---|
| G1 | `relation_to_host_repo` | How it overlaps/contrasts with subject 09 (`ai-memory`) | prose, ≤ 3 sentences |
| G2 | `open_questions` | What the researcher could not resolve | bulleted list |

## Filling rules

- **Cite or mark unknown.** No estimates without a source.
- **One value per cell** unless format says otherwise.
- **Use the same units** across all subjects (ms for latency, tokens for context cost).
- If a system has multiple modes (e.g., local + cloud), pick the default and
  note variants in long-form prose below the table.
