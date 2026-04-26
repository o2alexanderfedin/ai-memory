# Finding 03 — Memsearch (Zilliz)

- **Subject:** memsearch (zilliztech/memsearch)
- **Pinned commit:** `a3e621f63d52b65de2427cb5aadb65a6d95af3ab` (2026-04-25)
- **Researcher:** #03
- **Date:** 2026-04-25

## DIMENSIONS

| # | Dimension | Value |
|---|---|---|
| A1 | name | memsearch |
| A2 | vendor_or_author | Zilliz Inc. (lead: Cheney Zhang) |
| A3 | license | MIT |
| A4 | source_availability | public-repo |
| A5 | video_level | 3 |
| A6 | maturity | active |
| B1 | storage_backend | hybrid:markdown-files+vector-db:milvus |
| B2 | retrieval_mechanism | hybrid:dense+bm25+rrf |
| B3 | write_path | auto-extracted |
| B4 | update_model | append-only |
| B5 | memory_unit | chunk |
| B6 | schema_shape | semi-structured |
| C1 | write_latency | unknown |
| C2 | read_latency | unknown |
| C3 | recall_accuracy | 0.776 R@5 zh / 0.814 R@5 en (bge-m3 ONNX int8 on memsearch internal benchmark, 955 chunks × 2172 queries) |
| C4 | scale_ceiling | unknown (Milvus Lite single-file → Milvus Server → Zilliz Cloud auto-scale) |
| C5 | token_overhead_per_turn | unknown (cold-start: last 30 lines × 2 most-recent daily logs as `additionalContext`; per-turn hint is one-line `systemMessage`) |
| C6 | cost_model | self-host free (ONNX local) / OpenAI-style embedding API per-token / Zilliz Cloud free tier + paid tiers |
| D1 | cc_integration | hook + slash-command (4 lifecycle hooks + memory-recall skill in `context: fork` subagent) |
| D2 | other_clients | openclaw, opencode, codex-cli |
| D3 | protocols | none (shells out to memsearch CLI; Python API also exposed) |
| D4 | lock_in_level | low |
| D5 | composability | composes-with:openclaw,opencode,codex-cli |
| E1 | setup_complexity | 1 |
| E2 | maintenance_burden | low |
| E3 | observability | mixed (logs via `claude --debug`, status line via `systemMessage`, CLI `stats`/`config list --resolved`, watcher PID file) |
| E4 | failure_modes | First-run hang while ONNX model (~558 MB) downloads from HuggingFace; Milvus Lite is single-writer so concurrent agents need Server/Cloud; orphaned watcher PID files if Claude SIGKILL'd. |
| E5 | data_locality | mixed (default local-only; opt-in Zilliz Cloud / OpenAI / Voyage / Jina / Mistral / Google sends data out) |
| E6 | privacy_posture | API keys read from env vars only, never persisted. Hidden files skipped during scan. No multi-tenancy: collection isolation is per-project (`ms_<plugin>_<projectname>`); no row-level ACL. |
| F1 | best_fit | Multi-agent developer who wants persistent semantic recall across Claude Code / Codex / OpenClaw / OpenCode with markdown source-of-truth and zero-config local default. |
| F2 | anti_patterns | Workflows that need structured graph traversal, entity-typed queries, or cross-user/team ACLs — memsearch is single-user and unstructured. |
| F3 | not_for | Agents that need typed knowledge graphs, real-time multi-writer collaboration on a shared local index, or sub-millisecond latency at billion-record scale (Milvus Lite cap). |
| F4 | evidence_links | • README: `3rd-party/memsearch/README.md`<br>• Architecture: `3rd-party/memsearch/docs/architecture.md`<br>• Design philosophy: `3rd-party/memsearch/docs/design-philosophy.md`<br>• Embedding eval: `3rd-party/memsearch/evaluation/README.md`<br>• Claude Code plugin: `3rd-party/memsearch/plugins/claude-code/README.md`<br>• Upstream: https://github.com/zilliztech/memsearch |
| G1 | relation_to_host_repo | Both treat persistent memory as first-class for AI coding agents, but `ai-memory` (subject 09) is the host project's own framework, while memsearch is a Zilliz-backed semantic-search library that could plug under `ai-memory` as a retrieval backend (markdown-on-disk + Milvus). They overlap on the "markdown is source of truth" stance and could compose rather than compete. |
| G2 | open_questions | • Numeric write/read latency in ms (no published figures).<br>• Token overhead per turn (cold-start size depends on user activity).<br>• Documented record-count ceilings for Milvus Lite mode.<br>• No third-party benchmark (LoCoMo, MemBench) — only internal evaluation. |

---

## Long-form notes (≤ 800 words)

### What it is

memsearch is a **markdown-first, Milvus-backed semantic memory layer** for AI coding agents, published by Zilliz under MIT. It positions itself as a *cross-platform* drop-in: one library and CLI, four official plugins (Claude Code, OpenClaw, OpenCode, Codex CLI). The repo is young (first commit 2026-02-09) but very active — 329 commits in ~10 weeks, 1.4k stars, 6 open issues, ten contributors with one dominant author (Cheney Zhang). v0.4.0 shipped 2026-04-22.

### Architecture (Level 3 with markdown veneer)

The system has two surfaces:
1. **Source of truth:** plain `.memsearch/memory/YYYY-MM-DD.md` files containing per-session bullet summaries with HTML-comment anchors `<!-- session:UUID turn:UUID transcript:/path/to/jsonl -->`. Human-readable, git-friendly, rebuildable.
2. **Derived index:** a Milvus collection (`memsearch_chunks`) with both a dense `FLOAT_VECTOR` field and an auto-generated BM25 `SPARSE_FLOAT_VECTOR`. Chunks are heading-bounded markdown sections (max 1500 chars, 2-line overlap). Primary key is a SHA-256 composite ID over `source:lines:contentHash:model`, so the hash *is* the dedup key — no sidecar SQLite. Unchanged content makes zero embedding API calls on re-index.

Search is **hybrid (dense cosine + BM25) fused with Reciprocal Rank Fusion (k=60)** in a single Milvus query. Three deployment tiers share the same API: Milvus Lite (single `.db` file, default), self-hosted Milvus Server, or Zilliz Cloud (free tier).

### Claude Code integration

Pure-hook, no MCP. Four shell hooks plus one skill:
- **SessionStart** — boot a `memsearch watch` singleton (1500ms debounce file watcher), inject the last 30 lines of the 2 most recent daily logs as `additionalContext`, write a `## Session HH:MM` heading, post a status line via `systemMessage`.
- **UserPromptSubmit** — single-line hint `[memsearch] Memory available` (skipped under 10 chars).
- **Stop** (async, 120s timeout) — extract last turn from JSONL via inline Python (no `jq`), pipe to `claude -p --model haiku` for a 2-6 bullet third-person summary, append to today's `.md` with anchor, run `memsearch index`.
- **SessionEnd** — kill the watcher.

Recall is delegated to a **memory-recall skill running in a forked subagent** (`context: fork`). The subagent performs the three-layer disclosure — L1 `memsearch search` → L2 `memsearch expand <chunk_hash>` (full markdown section) → L3 `memsearch transcript` (raw JSONL drilldown) — and returns *only* a curated summary to the main context. No MCP tool definitions consume context tokens.

### Embedding choice

The default is **ONNX bge-m3 int8** (558 MB, gpahal/bge-m3-onnx-int8), CPU-only, no API key. The repo's `evaluation/README.md` documents an in-house benchmark of 12 models on 955 chunks × 2172 bilingual queries; bge-m3 (PyTorch) tops it (zh R@5 0.783 / en R@5 0.815) and the int8 ONNX variant is within 1.1% (0.776 / 0.814) at a quarter of the size, beating OpenAI text-embedding-3-small (0.717 / 0.767). Pluggable: OpenAI, Google, Voyage, Jina, Mistral, Ollama, sentence-transformers, ONNX.

### Strengths vs. failure modes

Strengths: zero-config local default, true cross-platform (you can switch agent and keep memory), markdown portability eliminates lock-in, hybrid search is genuinely better than dense-only for code/error-code/config-value lookups, content-hash dedup means re-indexing is free.

Failure modes: first session hangs while the 558 MB model downloads from HuggingFace (mitigated with `HF_ENDPOINT` mirror); Milvus Lite is single-writer so live `watch` falls back to one-time index-on-start (push to Zilliz Cloud or self-hosted Milvus for real-time); orphaned watcher PIDs after SIGKILL; Stop hook depends on `claude -p --model haiku` succeeding — if the API key is missing the daily file shows `## Session` headings but no bullets.

### Relation to subject 09 (`ai-memory`)

memsearch is a credible **retrieval backend** that the host repo could compose with rather than compete against — both share the markdown-as-source-of-truth philosophy, both target Claude Code, but memsearch is purely a vector/hybrid recall layer and is agnostic to the agent identity / multi-tenancy concerns the host repo is building toward (the `tenant_id` enforcement from recent commits has no analog here).

### Open questions

No published latency numbers, no third-party benchmark (only internal), no documented record-count ceilings for Milvus Lite, and the cold-start `additionalContext` token cost depends on user history (no documented average).
