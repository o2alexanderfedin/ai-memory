# memsearch — quick notes

- **Upstream:** https://github.com/zilliztech/memsearch
- **Pinned commit:** `a3e621f63d52b65de2427cb5aadb65a6d95af3ab` (2026-04-25)
- **License:** MIT
- **Maturity:** active — 329 commits since 2026-02-09, 1.4k stars, 6 open issues, v0.4.0 released 2026-04-22

## What it is

Markdown-first semantic memory for AI coding agents (Claude Code, OpenClaw, OpenCode, Codex CLI). Source of truth is `.memsearch/memory/YYYY-MM-DD.md`; Milvus is a derived hybrid index (dense + BM25 + RRF k=60). Chunk dedup is content-addressable via SHA-256 — re-indexing unchanged content makes zero API calls.

## Files worth re-reading

- `README.md` (the canonical pitch — feature matrix, install, examples)
- `docs/architecture.md` (collection schema, hybrid search, deployment tiers, dedup)
- `docs/design-philosophy.md` (markdown-as-source-of-truth rationale, OpenClaw lineage)
- `evaluation/README.md` (12-model embedding benchmark, why ONNX bge-m3 int8 is the default)
- `plugins/claude-code/README.md` (the 4-hook + 1-skill design, forked-subagent recall, comparison vs claude-mem and CLAUDE.md)
- `src/memsearch/{core,chunker,store,scanner,watcher}.py` (engine internals)

## Notable claims

- bge-m3 ONNX int8 (558 MB, CPU): zh R@5 0.776 / en R@5 0.814 on internal 955-chunk benchmark — beats OpenAI text-embedding-3-small at zero cost.
- Three Milvus tiers (Lite single-file → Server → Zilliz Cloud) share identical API; switch via one URI.
- No MCP, no sidecar service: pure shell hooks calling the `memsearch` CLI; recall runs in `context: fork` subagent so intermediate results never enter main context.
