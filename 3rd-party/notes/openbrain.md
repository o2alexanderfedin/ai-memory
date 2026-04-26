# OpenBrain (OB1)

- **Upstream:** https://github.com/NateBJones-Projects/OB1
- **Pinned commit:** `7bbc37e274d1b3cbfbd35049f7174a46042765e9` (2026-04-21)
- **Clone path:** `3rd-party/openbrain/` (gitignored)
- **License:** FSL-1.1-MIT (Functional Source, becomes MIT after 2 years)
- **Survey finding:** [`cc-memory-systems-survey/findings/08-openbrain.md`](cc-memory-systems-survey/findings/08-openbrain.md)

## What it is

A remote MCP-server "single brain" for all AI tools. Storage is Supabase Postgres + pgvector (HNSW cosine, 1536-dim). The whole runtime is one ~400 LOC Deno Edge Function (`server/index.ts`) exposing four tools: `search_thoughts`, `list_thoughts`, `thought_stats`, `capture_thought`. Embedding + metadata extraction go to OpenRouter (`text-embedding-3-small`, `gpt-4o-mini`). Auth is a single shared `MCP_ACCESS_KEY` via header or query param.

Memory unit: a "thought" — `(content, embedding, jsonb metadata, sha256 fingerprint)`. Dedup is fingerprint upsert with JSONB merge.

## Why we cloned it

Subject 08 of the Claude Code Memory Systems Survey (Level 6 — "single brain for ALL your AI tools"). Cross-reference vs. subject 07 (Mem0).

## Files worth re-reading

- `server/index.ts` — the entire MCP runtime in one file
- `docs/01-getting-started.md` — schema, indexes, RLS, `match_thoughts`/`upsert_thought` SQL
- `CLAUDE.md` — guard rails for AI coding tools editing this repo
- `recipes/`, `skills/`, `extensions/` — agentic compounding layer

## Key differentiator vs. Mem0

Single-user, opinionated stack (Supabase + pgvector + OpenRouter), MCP-first, append+dedup (no LLM-driven update/delete). Mem0 is multi-actor, model-agnostic, library-embeddable, with semantic update reconciliation. OB1's product is the curated 6-extension learning path more than the code.
