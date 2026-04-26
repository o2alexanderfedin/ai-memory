# Mem0

- Upstream: https://github.com/mem0ai/mem0
- Pinned commit: `bd9d27ff509f6259c3bfd1915ca4c975db798c8a` (main, 2026-04-25)
- License: Apache-2.0 (SDK + server); proprietary hosted Platform.
- Slug: `mem0` (CC Memory Systems Survey, subject 07).

## What it is
Apache-2.0 memory layer for AI agents — `pip install mem0ai`. LLM extracts facts from message arrays (`gpt-5-mini` default), embeds them, stores in a pluggable vector store (Qdrant default; 20+ supported including pgvector, Pinecone, Weaviate, Milvus, Chroma, Redis, Faiss). Retrieval = semantic + BM25 + entity-boost fused, optional reranker. Polyglot monorepo with Python + TS SDKs, FastAPI server, Claude Code / Cursor / Codex plugin, OpenClaw plugin, Vercel AI provider.

## v3 break (April 2026)
- ADD-only — no UPDATE/DELETE in extraction.
- **Graph memory REMOVED** (was Neo4j/Memgraph/Kuzu/AGE/Neptune). Replaced by retrieval-time entity linking.
- New benchmarks: LoCoMo 91.6, LongMemEval 93.4, BEAM-1M 64.1, BEAM-10M 48.6; ~7K tokens/retrieval, ~1s p50.

## Claude Code
First-class. `/plugin install mem0@mem0-plugins` installs MCP server (`https://mcp.mem0.ai/mcp`, 9 tools) + lifecycle hooks (SessionStart/UserPromptSubmit/PreCompact/Stop/SessionEnd) + skill.

## Files worth re-reading
- `mem0/memory/main.py` — engine.
- `mem0/utils/scoring.py`, `entity_extraction.py` — v3 retrieval.
- `mem0-plugin/`, `openclaw/`.
- `MIGRATION_GUIDE_v1.0.md`.
