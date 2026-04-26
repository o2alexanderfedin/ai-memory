# Findings 01 — Native Claude Code memory

Subject: Claude Code's built-in memory layer (CLAUDE.md hierarchy, `.claude/rules/`, `/memory`, and auto memory). Slug: `native-claude-code`. Video level: **1**.

All citations resolve to the official docs at `https://code.claude.com/docs/en/...` (the `docs.claude.com/en/docs/claude-code/...` URLs in the brief 301-redirect to this host).

## Dimension table

| # | Dimension | Value | Source |
|---|---|---|---|
| A1 | `name` | Claude Code memory (CLAUDE.md + auto memory) | [memory] |
| A2 | `vendor_or_author` | Anthropic | [overview] |
| A3 | `license` | proprietary | [overview] (closed-source CLI) |
| A4 | `source_availability` | docs-only | brief; no public source repo |
| A5 | `video_level` | 1 | brief |
| A6 | `maturity` | active (auto memory shipped in v2.1.59; docs continuously updated) | [memory] "Auto memory requires Claude Code v2.1.59 or later" |
| B1 | `storage_backend` | markdown-files (CLAUDE.md, CLAUDE.local.md, `.claude/rules/*.md`, `~/.claude/projects/<project>/memory/MEMORY.md` + topic files) | [memory] |
| B2 | `retrieval_mechanism` | hybrid: full-text injection at launch + agentic-search (Claude reads topic files on-demand with its file tools) | [memory] |
| B3 | `write_path` | hybrid: manual (you edit CLAUDE.md) + agentic (Claude writes auto memory) | [memory] "Who writes it: You / Claude" |
| B4 | `update_model` | overwrite (markdown edits in place); no version history beyond git for committed CLAUDE.md | [memory] |
| B5 | `memory_unit` | file (one markdown document per scope/topic) | [memory] |
| B6 | `schema_shape` | semi-structured (markdown headers/bullets; YAML frontmatter `paths:` for `.claude/rules/`) | [memory] path-specific rules section |
| C1 | `write_latency` | unknown (local file write; not benchmarked publicly) | — |
| C2 | `read_latency` | unknown (loaded once at session launch from local disk) | — |
| C3 | `recall_accuracy` | unknown (no published benchmark; docs explicitly note "no guarantee of strict compliance") | [memory] troubleshoot section |
| C4 | `scale_ceiling` | Soft: target **<200 lines per CLAUDE.md**; MEMORY.md startup load capped at **first 200 lines or 25 KB, whichever first**; `@`-import recursion **max depth 5 hops**; invoked-skill bodies after `/compact` capped at **5,000 tokens/skill and 25,000 tokens total** | [memory], [context-window] |
| C5 | `token_overhead_per_turn` | Per-session, not per-turn. Illustrative figures from the official context-window visualization: system prompt ≈ **4,200**; MEMORY.md ≈ **680**; `~/.claude/CLAUDE.md` ≈ **320**; project CLAUDE.md ≈ **1,800** ("Token counts are illustrative. Actual values vary"). Loaded once per session; persists for every turn until `/compact`. | [context-window] |
| C6 | `cost_model` | Bundled with Claude Code subscription; cost driver = tokens consumed by injected memory files in every Claude API call of the session | [overview] pricing; [memory] |
| D1 | `cc_integration` | native (`CLAUDE.md`, `/memory`, `/init`, `@import` syntax, `.claude/rules/`, `claudeMdExcludes`, `autoMemoryEnabled` setting) | [memory] |
| D2 | `other_clients` | none — files are CC-specific (note: AGENTS.md cross-import is a workaround, not a shared loader) | [memory] AGENTS.md section |
| D3 | `protocols` | none (filesystem convention only; no API) | [memory] |
| D4 | `lock_in_level` | low — content is plain markdown the user owns; portable to any tool, only the loader is proprietary | [memory] |
| D5 | `composability` | composes-with most other entries (skills, hooks, MCP, subagents), often functions as the substrate the rest extend | [memory], [overview] |
| E1 | `setup_complexity` | 1 (drop-in: create `CLAUDE.md` or run `/init`) | [memory] |
| E2 | `maintenance_burden` | low (periodic pruning of CLAUDE.md and auto memory recommended) | [memory] |
| E3 | `observability` | mixed: `/memory` lists loaded files; `/context` shows live token breakdown; `InstructionsLoaded` hook logs which files load and why | [memory], [context-window] |
| E4 | `failure_modes` | Instructions silently ignored when CLAUDE.md is too long, conflicting, or excluded by `claudeMdExcludes`; nested CLAUDE.md not re-injected after `/compact` until the matching subdirectory is touched again. | [memory] troubleshoot, [context-window] |
| E5 | `data_locality` | local-only (markdown lives on user's machine; auto memory not synced across machines) | [memory] "Auto memory is machine-local" |
| E6 | `privacy_posture` | Files sit on local disk; whatever is in them is sent to Claude's API on every relevant turn. CLAUDE.local.md is gitignored by convention; managed-policy CLAUDE.md cannot be excluded per-user. | [memory] |
| F1 | `best_fit` | Persistent, repo-shared coding standards, build/test commands, and personal preferences for a single developer or team using Claude Code. | [memory] |
| F2 | `anti_patterns` | Stuffing large reference docs, multi-step playbooks, or one-off task instructions into CLAUDE.md (use skills or path-scoped rules instead). | [memory] write-effective + skills note |
| F3 | `not_for` | Cross-machine sync, semantic search over thousands of memories, structured/typed knowledge graphs, or any workload that needs guaranteed compliance (it's context, not enforcement). | [memory] |
| F4 | `evidence_links` | • https://code.claude.com/docs/en/memory<br>• https://code.claude.com/docs/en/overview<br>• https://code.claude.com/docs/en/sub-agents#enable-persistent-memory<br>• https://code.claude.com/docs/en/context-window | — |
| G1 | `relation_to_host_repo` | The host `ai-memory` repo aims at richer, queryable memory; native CC memory is the default surface it complements/competes with. Native memory is markdown-in-context; `ai-memory` adds structured retrieval, multi-tenant scoping, and APIs the markdown loader lacks. | self |
| G2 | `open_questions` | • Exact `write_latency`/`read_latency` numbers (Anthropic publishes none).<br>• Whether `MEMORY.md` updates are atomic vs. last-write-wins across concurrent sessions.<br>• Token cost of CLAUDE.md after `--append-system-prompt` interaction.<br>• Public benchmark scores (LoCoMo, MemBench) — none published. | — |

`unknown` count: **3** (C1 write_latency, C2 read_latency, C3 recall_accuracy). Reason: Anthropic publishes no latency numbers or compliance benchmarks for the memory loader; the docs explicitly disclaim "no guarantee of strict compliance" rather than quoting a recall score.

## Analysis

Native Claude Code memory is the simplest possible memory architecture: **plain markdown files on the local filesystem, concatenated into the conversation at session start.** It has no database, no vector store, no embedding model, and no retrieval algorithm beyond "walk the directory tree and read what you find." That minimalism is both its strength and the reason every other entry in this survey exists.

**Two complementary subsystems.** CLAUDE.md is human-authored ("instructions you write"); auto memory is Claude-authored ("notes Claude writes itself"). Both load every session, but they sit in different files and have different size rules. CLAUDE.md files load **in full regardless of length**, while MEMORY.md is truncated at "the first 200 lines or 25 KB, whichever comes first." Topic files in the auto-memory directory (`debugging.md`, `api-conventions.md`, …) are **not** loaded at startup — Claude reads them on demand with its file tools, which is the closest the system gets to retrieval.

**Hierarchy.** Four scopes, more-specific overrides more-general: managed policy (e.g., `/Library/Application Support/ClaudeCode/CLAUDE.md`) → project (`./CLAUDE.md` or `./.claude/CLAUDE.md`) → user (`~/.claude/CLAUDE.md`) → local (`./CLAUDE.local.md`, gitignored). Claude walks **upward** from cwd, concatenating every CLAUDE.md and CLAUDE.local.md it finds; CLAUDE.local.md is appended *after* CLAUDE.md at each level so personal notes win on conflict. Files in **subdirectories** below cwd are not loaded at launch — they enter context only when Claude reads a file in that directory.

**Imports and rules.** CLAUDE.md supports `@path/to/file` imports with **maximum recursion depth of five hops**. Imports are convenience, not optimization — imported content still loads at launch and counts against the context budget. For modular organization without unconditional loading, `.claude/rules/*.md` files with YAML `paths:` frontmatter act as path-scoped rules that trigger only when Claude reads a matching file.

**Token cost.** The official context-window visualization gives illustrative figures: system prompt ≈ 4,200 tokens, MEMORY.md ≈ 680, user CLAUDE.md ≈ 320, project CLAUDE.md ≈ 1,800. These are paid **once per session** (re-injected after `/compact`) and remain in the active window every turn. The docs explicitly recommend keeping each CLAUDE.md under 200 lines — both for token economy and because "longer files consume more context and reduce adherence."

**Subagents.** Subagents do **not** inherit the parent's auto memory; they get their own MEMORY.md if `memory:` frontmatter is set (`user`, `project`, or `local` scopes; storage at `~/.claude/agent-memory/<name>/` or analogous). They **do** load the project CLAUDE.md ("the subagent loads CLAUDE.md too. Same file, same content, but it counts against the subagent's context"), unless they're the built-in Explore/Plan agents which skip it.

**Compaction behavior.** Project-root CLAUDE.md and unscoped rules are **re-injected from disk** after `/compact`. Nested CLAUDE.md and path-scoped rules are **lost until** a matching file is read again. This is the most subtle gotcha and the source of most "instruction disappeared" reports.

**Where it sits in the taxonomy.** This is the Level 1 baseline against which every richer memory system in the survey will be measured. It costs nothing extra, leaks zero data beyond the conversation it's already in, and requires no setup. It cannot do semantic recall, cross-machine sync, or structured queries — gaps that motivate Levels 2-6.

[memory]: https://code.claude.com/docs/en/memory
[overview]: https://code.claude.com/docs/en/overview
[context-window]: https://code.claude.com/docs/en/context-window
