# MemPalace — research notes

Pinned commit: `5e574045028d1b6fb9ead3569cdf21c47bd3c4df` (2026-04-25).
Upstream: https://github.com/MemPalace/mempalace — MIT, Python 3.9+.
PyPI: `pip install mempalace`. Dep: ChromaDB only for core path.

## What to re-read first

- `README.md`, `CLAUDE.md`, `MISSION.md` — claims and design principles.
- `benchmarks/BENCHMARKS.md` — every published number plus an unusually
  honest "Benchmark Integrity" section (the 100% LongMemEval and LoCoMo
  top-50 results are explicitly disclosed as contaminated).
- `docs/HISTORY.md` — retractions and scam-domain notice.
- `docs/CLOSETS.md` — index layer (closets = pointer lines into drawers).
- `mempalace/searcher.py` — hybrid BM25 + vector + closet-first pipeline.
- `mempalace/palace.py` — wings/rooms/drawers/closets primitives.
- `mempalace/knowledge_graph.py` — SQLite temporal triple store.
- `mempalace/backends/base.py` — RFC-001 backend ABC (Postgres/LanceDB
  are v4-alpha, not shipped).

## Surprises

- "Self-organising" is regex + heuristics, not autonomous LLM clustering.
  LLM-routed indexing (palace v1) collapsed to 34.2% R@5; the working
  variant uses deterministic keyword routing against index-time
  summaries.
- The 96.6% raw LongMemEval R@5 baseline beats most competitors with
  zero LLM calls.
- Hooks (`hooks/mempal_*.sh`) are the recommended capture path for
  Claude Code; they auto-mine the JSONL transcript without spending
  chat tokens.

## Status

Active. v3.3.3 stable; v4.0.0-alpha in flight (pluggable backends,
local NLP, hybrid retrieval).
