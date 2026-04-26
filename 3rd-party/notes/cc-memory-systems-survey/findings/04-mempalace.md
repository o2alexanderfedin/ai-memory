# Findings 04 — MemPalace

**Subject:** MemPalace
**Slug:** `mempalace`
**Repo:** https://github.com/MemPalace/mempalace
**Pinned commit:** `5e574045028d1b6fb9ead3569cdf21c47bd3c4df` (2026-04-25)
**Researcher:** Researcher #04
**Date:** 2026-04-25

## Dimensions table

| # | Dimension | Value |
|---|---|---|
| A1 | name | MemPalace |
| A2 | vendor_or_author | Milla Jovovich + Ben Sigman (`bensig`) + community contributors (MemPalace org) |
| A3 | license | MIT |
| A4 | source_availability | public-repo |
| A5 | video_level | 5 |
| A6 | maturity | active (v3.3.3 on PyPI; first commit 2026-04-04, 617 commits in ~3 weeks, dozens of contributors, dependabot, CI on Linux/macOS/Windows) |
| B1 | storage_backend | hybrid:vector-db:chromadb+sqlite (Chroma for drawers/closets; SQLite for temporal knowledge graph; pluggable backend interface for Postgres/LanceDB on roadmap) |
| B2 | retrieval_mechanism | hybrid:semantic+keyword (ChromaDB cosine vector + Okapi BM25 re-rank; closet-index pre-pass; optional LLM re-rank) |
| B3 | write_path | hybrid (CLI `mempalace mine` is manual/scripted; auto-save Stop + PreCompact hooks invoke mining on the JSONL transcript automatically; closets/entities are extracted by regex + heuristics, not LLMs) |
| B4 | update_model | append-only for drawers; per-source-file purge-and-rewrite for closets on re-mine; versioned via `NORMALIZE_VERSION` for silent rebuilds |
| B5 | memory_unit | chunk (~800-char verbatim "drawer"; closet line = topic+entities+→drawer-id pointer; KG triple separately) |
| B6 | schema_shape | semi-structured (verbatim text drawers + typed metadata: wing/room, source_file, mtime; KG is typed-schema entities/triples with `valid_from`/`valid_to`) |
| C1 | write_latency | unknown (no published per-drawer mine latency; design budget "Hooks under 500ms" per CLAUDE.md is for hook overhead, not write throughput) |
| C2 | read_latency | unknown (no benchmark publishes wall-clock retrieval; "Startup injection under 100ms" budget for L0+L1 wake-up only) |
| C3 | recall_accuracy | 96.6%@LongMemEval-R@5 (raw, no LLM, full 500q); 98.4%@LongMemEval-R@5 (hybrid_v4, held-out 450q); 88.9%@LoCoMo-R@10 (hybrid_v5, top-10); 92.9%@ConvoMem-recall; 80.3%@MemBench-R@5 |
| C4 | scale_ceiling | unknown headline limit; reports of palaces with 50K–200K drawers from backfilling Claude Code history; HNSW index bloat fix (#346) targets palaces where Chroma's index grew to 441 GB |
| C5 | token_overhead_per_turn | ~600–900 tokens for L0+L1 wake-up (identity + auto-generated essential story); per-search overhead is the returned drawer text (verbatim, not summarized); claim "zero extra tokens" for background hooks (filing happens out-of-chat) |
| C6 | cost_model | self-host, free for core (no API key required for raw 96.6% path); optional LLM re-rank ~$0.001/query Haiku, ~$0.003/query Sonnet; ~300 MB disk for default ONNX embedding model |
| D1 | cc_integration | mixed: MCP-server (`mempalace-mcp`, 19–29 tools), hook (Stop + PreCompact shell scripts), slash-command (Claude Code plugin: `/mempalace:init`, `:search`, `:mine`, `:status`, `:help`), external-CLI (`mempalace`) |
| D2 | other_clients | Codex CLI (OpenAI), Gemini CLI, AnythingLLM (MCP ping shim), any MCP-compatible client |
| D3 | protocols | MCP, plus its own Python API and CLI |
| D4 | lock_in_level | low (MIT, all data lives locally in ChromaDB + SQLite, exporter ships with the package, backend is an ABC so storage is swappable) |
| D5 | composability | competes-with: mem0, mastra, supermemory, hindsight, zep (all positioned as alternatives in benchmarks/BENCHMARKS.md); composes-with: any MCP host (Claude Code, Codex, Gemini CLI) |
| E1 | setup_complexity | 2 (`pip install mempalace && mempalace init <dir>`; `claude plugin install` route is even closer to drop-in, but a vector-store dependency and ~300 MB embedding model still have to download) |
| E2 | maintenance_burden | low (local SQLite + Chroma; auto-repair, dedup, migrate, and consistency-check tools shipped; HNSW bloat / Chroma version migration are known recurring issues) |
| E3 | observability | mixed (CLI `status`, `repair`, `export`; hook log at `~/.mempalace/hook_state/hook.log`; per-question result JSONLs in benchmarks; no dashboard or metrics endpoint) |
| E4 | failure_modes | Closet regex extractor is shallow (5,000-char window, narrative content gets weak topics) so it falls back to direct drawer search; ChromaDB HNSW index file can bloat dramatically and Chroma 0.6→1.5 migration has crashed mid-mine; Windows path / encoding issues fixed repeatedly. |
| E5 | data_locality | local-only (no telemetry, no cloud sync; "physically cannot send your data" per design principles) |
| E6 | privacy_posture | Local-first by architecture; query sanitizer mitigates prompt-injection from mined content; KG SQLite directory is chmod 700; no PII redaction or encryption-at-rest beyond the user's own filesystem permissions. |
| F1 | best_fit | A solo developer or small team using Claude Code (or another MCP client) on a single workstation who wants every conversation and every project file kept verbatim, fully offline, with hybrid semantic+keyword recall and an optional LLM re-rank. |
| F2 | anti_patterns | Multi-user / multi-tenant deployments; teams that need cloud sync today (LanceDB/Postgres backends are roadmap, not shipped); workloads requiring extracted/structured fact memory (the project explicitly refuses to summarize). |
| F3 | not_for | Server-side memory shared across users; environments where verbatim retention of conversation text is a compliance liability; agents that need cross-device continuity without manual file sync. |
| F4 | evidence_links | - https://github.com/MemPalace/mempalace (README, CLAUDE.md, MISSION.md, ROADMAP.md)<br>- `benchmarks/BENCHMARKS.md` (LongMemEval/LoCoMo/ConvoMem/MemBench numbers + integrity disclosures)<br>- `docs/HISTORY.md` (post-launch retractions, scam-domain notice)<br>- `docs/CLOSETS.md` (index layer)<br>- `mempalace/searcher.py`, `palace.py`, `knowledge_graph.py`, `backends/base.py`<br>- `.claude-plugin/plugin.json`, `hooks/README.md`, `examples/mcp_setup.md` |
| G1 | relation_to_host_repo | `ai-memory` is a server-first multi-tenant memory service; MemPalace is the diametric opposite — local-only, single-user, no API key, MIT. They overlap on "give an MCP client durable memory" but contrast on tenancy, deployment, and (most loudly) on whether to extract memories at all. MemPalace's headline thesis ("raw verbatim text beats LLM extraction") is a direct challenge to any extractor-based design `ai-memory` adopts. |
| G2 | open_questions | - No published write-side latency or per-drawer mine throughput.<br>- Scale ceiling is anecdotal (50K–200K drawers); no upper bound documented.<br>- Postgres / LanceDB backends and multi-device sync are v4-alpha roadmap, not shipped.<br>- LongMemEval headline 96.6% is retrieval recall, not end-to-end QA accuracy; no QA-accuracy number is published.<br>- "29 MCP tools" (README) vs "19 MCP tools" (plugin manifest) — actual tool count not verified in this pass. |

## Long-form discussion

### What it actually is

MemPalace is the local-first counterargument to LLM-driven memory. It stores
the full conversation verbatim, never summarises, and retrieves with hybrid
vector + BM25 search. The "self-organisation" pitched in the Level-5 video
is a regex/heuristic structuring layer on top of ChromaDB, not autonomous
agentic clustering. New content is filed into a four-level hierarchy:

```
WING (person/project) → ROOM (day/topic) → DRAWER (verbatim chunk) → CLOSET (index pointers)
```

Wings come from the project config (`mempalace.yaml`) or from the entity
detector (capitalised proper nouns minus a stoplist). Rooms are
date/topic groupings derived from filenames and content. Drawers are
~800-char chunks with 100-char overlap. Closets are short pointer lines
of the form `topic|entities|→drawer_a,drawer_b`, capped at 1,500 chars
each, extracted by regex over the first 5,000 chars of the source. The
"AAAK" compression dialect (`mempalace/dialect.py`) is a symbolic
shorthand for the index layer — *not* lossy compression of user
content.

A separate temporal knowledge graph (`mempalace/knowledge_graph.py`)
runs in parallel: `(subject, predicate, object, valid_from, valid_to)`
triples in SQLite, populated by `general_extractor.py` /
`entity_detector.py` / `fact_checker.py`. This is what they pitch as
the Zep-equivalent.

### Self-organisation, honestly

It is structured ingest plus pluggable LLM-assist, not autonomous
reorganisation. The miner runs deterministic regex extraction at write
time; LLM involvement at index time (`closet_llm.py`,
`general_extractor.py`, `room_detector_local.py`) is feature-flagged
and optional. The optional "diary mode" (98.2% R@5 with 65% Haiku
cache) is the closest the project gets to LLM-driven summarisation,
and the project's own `BENCHMARKS.md` is unusually frank that
LLM-routed indexing (palace v1) tanked recall to 34.2% — terminology
mismatch between independent LLM calls. The fix was deterministic
keyword routing against the index-time summaries.

### Capture cadence

Two Claude Code hooks drive write cadence:
`mempal_save_hook.sh` fires on Stop every 15 human messages and
auto-mines the JSONL transcript; `mempal_precompact_hook.sh` fires on
PreCompact and force-saves before the context window collapses. Both
"block" once with a `decision: block` reason so the agent writes its
own diary entry, then let the next Stop through via
`stop_hook_active`. Background mining means the chat window pays zero
extra tokens for filing — explicitly contrasted with v3, where
in-chat diary writes cost ~$1.13/session.

### Read path

`mempalace_search` (and the closet-first variant) hits the closets
collection first, parses the `→drawer_a,drawer_b` pointers, hydrates
those drawers, and applies a `max_distance` filter. If closets miss
or were never built (conversation-mined wings don't yet have closets),
the searcher falls back to direct drawer search. A four-layer wake-up
stack (`layers.py`) supplies L0 identity (~100 tokens) and L1
essential story (~500–800 tokens) at session start; L2/L3 are
on-demand and unbounded.

### Maturity and license

MIT, Python 3.9+, single dependency for the core path (ChromaDB).
Repo is barely three weeks old as of the pin (first commit
2026-04-04) but already has 617 commits, a marketplace plugin, a
PyPI release at 3.3.3, and a v4-alpha roadmap including Postgres,
LanceDB, and local-NLP backends. CI runs on Linux/macOS/Windows
with 85% coverage gate. The maintainers also publish an unusually
honest `docs/HISTORY.md` retracting earlier benchmark over-claims
(the "+34% palace boost" and the LoCoMo top-50 100% number) — a
strong maturity signal even though the project itself is young.

### Why it matters to this survey

MemPalace is the empirically strongest member of the "no LLM in the
hot path" camp. Its 96.6% raw R@5 on LongMemEval — verbatim text +
default ChromaDB embeddings, no extraction, no rerank — is a load-
bearing data point for any survey that wants to argue that
LLM-driven memory extraction is over-engineering. It also shows
that hybrid retrieval (BM25 + vector + simple regex preference
boosts) closes most of the remaining gap before any LLM is invoked.
