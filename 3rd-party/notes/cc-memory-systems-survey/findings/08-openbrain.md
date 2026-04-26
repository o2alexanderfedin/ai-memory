# Finding 08 — OpenBrain (OB1)

- **Resolved upstream:** https://github.com/NateBJones-Projects/OB1
- **Pinned commit:** `7bbc37e274d1b3cbfbd35049f7174a46042765e9` (2026-04-21)
- **Local clone:** `/Users/alexanderfedin/Projects/ai-memory/3rd-party/openbrain/`
- **Researched:** 2026-04-25

## Dimensions

| # | Dimension | Value |
|---|---|---|
| A1 | name | OpenBrain (a.k.a. OB1, "Open Brain") |
| A2 | vendor_or_author | Nate B. Jones (maintainer team; community-driven repo, admin Matt Hallett) |
| A3 | license | FSL-1.1-MIT (Functional Source License, becomes MIT after 2 years) |
| A4 | source_availability | public-repo |
| A5 | video_level | 6 |
| A6 | maturity | active (initial release 2026-03-11; 310 commits in ~6 weeks; ongoing PRs through 2026-04-21) |
| B1 | storage_backend | postgres (Supabase + pgvector); Kubernetes self-host variant via PostgreSQL+pgvector |
| B2 | retrieval_mechanism | hybrid:semantic+structured (HNSW cosine vector search via `match_thoughts` SQL function, plus JSONB metadata `@>` filtering on type/topic/person/date) |
| B3 | write_path | hybrid (manual prompt + auto-extracted metadata via gpt-4o-mini; ingestion recipes for ChatGPT/Obsidian/Gmail/Twitter/etc.) |
| B4 | update_model | merge (SHA-256 content fingerprint upsert; metadata JSONB merge on conflict) |
| B5 | memory_unit | record (a "thought": id, content, embedding, jsonb metadata, fingerprint, timestamps) |
| B6 | schema_shape | semi-structured (fixed `thoughts` row + free-form JSONB metadata with conventional fields: `type`, `topics[]`, `people[]`, `action_items[]`, `dates_mentioned[]`, `source`) |
| C1 | write_latency | unknown (one OpenRouter embedding call + one OpenRouter LLM extraction call + one Supabase upsert; cold Edge Function "few seconds" per docs) |
| C2 | read_latency | unknown (one embedding call + one HNSW SQL query; cold-start "a few seconds", warm calls faster — README claim, no number) |
| C3 | recall_accuracy | unknown (no benchmark) |
| C4 | scale_ceiling | unknown (bounded by Supabase free tier — 500MB DB, 5GB egress; no documented row ceiling) |
| C5 | token_overhead_per_turn | unknown (depends on `limit`/`threshold`; default `limit=10`, `threshold=0.5`) |
| C6 | cost_model | self-host: ~$0.10–$0.30/month operating cost (Supabase free tier + ~$5 OpenRouter credits "lasts months") per Nate B. Jones' newsletter |
| D1 | cc_integration | MCP-server (remote Streamable HTTP MCP, registered via `claude mcp add --transport http open-brain ...`) |
| D2 | other_clients | claude-desktop, chatgpt (paid + Developer Mode), claude-code, openai-codex, cursor, vscode-copilot, windsurf, gemini (via Custom GPT/Gem companion), plus Slack/Discord capture bots |
| D3 | protocols | MCP (Streamable HTTP via `@hono/mcp` + `@modelcontextprotocol/sdk`); REST (Supabase auto-generated) |
| D4 | lock_in_level | low (data is plain Postgres + pgvector; entire MCP server is one ~400-line Deno file under FSL/MIT; can re-point any pgvector instance) |
| D5 | composability | competes-with:mem0; composes-with:claude-code-builtin (CLAUDE.md skills directory present); supersedes:CLAUDE.md-only memory |
| E1 | setup_complexity | 3 (Supabase project + 6 SQL blocks + Supabase CLI + Edge Function deploy + OpenRouter key + MCP wiring; advertised "45 min, no coding") |
| E2 | maintenance_burden | low (managed Supabase + serverless Edge Function; key rotation + occasional schema migrations) |
| E3 | observability | logs (Supabase Edge Function logs + Supabase dashboard Table Editor); ui-dashboard via community SvelteKit/Next.js dashboards under `dashboards/` |
| E4 | failure_modes | 401 on access-key mismatch; "permission denied for table thoughts" on missing service_role grants; cold-start timeouts (>10s) with `mcp-remote`; OpenRouter credit exhaustion silently breaks capture/search. |
| E5 | data_locality | vendor-cloud (Supabase by default); self-host variant via Kubernetes + Postgres+pgvector under `integrations/kubernetes-deployment/` |
| E6 | privacy_posture | Single-tenant by default (one Supabase project per user); Row Level Security policy restricts the `thoughts` table to `service_role`; access key gates the public Edge Function URL; embeddings + metadata extraction call OpenRouter (third-party data egress). |
| F1 | best_fit | A solo knowledge worker who wants one shared persistent memory across Claude Desktop, ChatGPT, Claude Code, Cursor, etc., owns their data in Postgres, and is willing to deploy a Supabase Edge Function once. |
| F2 | anti_patterns | Teams needing native multi-tenant isolation out-of-the-box; air-gapped/no-internet environments (default flow assumes Supabase + OpenRouter SaaS); workloads requiring sub-100ms cold reads. |
| F3 | not_for | Project-scoped code memory (it stores user-level "thoughts," not repo state); non-MCP clients without a bridge; offline-first laptops. |
| F4 | evidence_links | - https://github.com/NateBJones-Projects/OB1 (README)<br>- /Users/alexanderfedin/Projects/ai-memory/3rd-party/openbrain/server/index.ts (MCP server)<br>- /Users/alexanderfedin/Projects/ai-memory/3rd-party/openbrain/docs/01-getting-started.md (schema + deploy flow)<br>- /Users/alexanderfedin/Projects/ai-memory/3rd-party/openbrain/CLAUDE.md (agent guard rails)<br>- https://www.simplenews.ai/news/ob1-open-brain-offers-dollar010month-personal-knowledge-infrastructure-for-ai-agents-ssf5 ($0.10/month claim)<br>- https://promptkit.natebjones.com/20260224_uq1_guide_main (setup guide) |
| G1 | relation_to_host_repo | OB1 is what the host `ai-memory` project would become if it (a) chose Supabase+pgvector instead of any local store, (b) shipped exclusively as a remote MCP server, and (c) refused to ship a SaaS. The host repo's tenant-scoped auth model (US-1.4) is more rigorous than OB1's single-key-per-brain gate. |
| G2 | open_questions | - No published latency or recall benchmarks.<br>- No documented multi-user story beyond "deploy a separate Supabase project per person" + the `primitives/rls/` guide.<br>- License: FSL-1.1-MIT explicitly forbids "competing" use; how this constrains a vendor that wants to embed OB1 is unclear. |

## Long-form notes (≤ 800 words)

### What it actually is

OpenBrain (the repo is named OB1 on GitHub) is a Level-6 "single brain for all your AI tools" stack assembled from off-the-shelf parts: Supabase Postgres with pgvector for storage, OpenRouter for embeddings (`openai/text-embedding-3-small`, 1536-dim) and metadata extraction (`openai/gpt-4o-mini`), and a single Deno-based Supabase Edge Function (`server/index.ts`, ~400 LOC) that exposes four MCP tools: `search_thoughts`, `list_thoughts`, `thought_stats`, `capture_thought`. Authentication is a single shared access key (`MCP_ACCESS_KEY`) checked on every request, accepted via `x-brain-key` header or `?key=` query param.

The data model is one table: `thoughts(id, content, embedding vector(1536), metadata jsonb, content_fingerprint, created_at, updated_at)` with an HNSW cosine index, GIN index on metadata, and a SHA-256 fingerprint unique index for dedup. Retrieval is a `match_thoughts` PL/pgSQL function that does vector similarity ranking with optional JSONB filter. Writes go through `upsert_thought`, which merges metadata on duplicate fingerprints rather than inserting twice.

### How it federates across clients

This is the differentiator. Because OB1 is a remote Streamable-HTTP MCP server, every MCP-capable client points to the same URL: Claude Desktop (Custom Connector), Claude Code (`claude mcp add --transport http`), ChatGPT (Developer Mode connector), OpenAI Codex (`mcp-remote` bridge in `~/.codex/config.toml`), Cursor / VS Code / Windsurf (via `supergateway` or `mcp-remote`). Every client reads and writes the same Postgres rows. Gemini integration is a "GEM" companion (a prompt persona, not MCP).

### Vs. Mem0 (subject 07) — the load-bearing differentiator

Both are Level-6 "shared memory for every AI tool." The split:

- **Architecture stance.** Mem0 ships an OSS Python SDK + a hosted SaaS plane; the OSS path supports many vector backends (Qdrant, Chroma, pgvector, Pinecone, etc.) and many LLMs/embedders, with multi-actor (`user_id`, `agent_id`, `run_id`) and a fact-extraction + reconciliation pipeline. OB1 is **opinionated to one stack**: Supabase + pgvector + OpenRouter, no SaaS. There is no business plane to sell to.
- **Multi-tenancy.** Mem0 is multi-actor by design. OB1 is **single-user-per-deployment**; the "share with family" story is to deploy a second Supabase project or run the `primitives/rls/` recipe by hand.
- **Memory operation model.** Mem0 reasons about memories: `add` runs LLM-driven ADD/UPDATE/DELETE/NONE decisions to keep the corpus consistent. OB1 is **append + dedup**: SHA-256 fingerprints prevent verbatim duplicates and merge metadata, but there is no semantic update/contradict step. Old beliefs and new beliefs both sit there at full weight.
- **Distribution.** Mem0 distributes as a library you embed. OB1 distributes as a **video-and-spreadsheet-shaped tutorial**: a credential-tracker `.xlsx`, a 27-min Vimeo walkthrough, a Substack post, and a recipes/extensions ladder ("Household KB → Family Calendar → Job Hunt"). The product is the curated learning path more than the code.
- **Agentic surface.** Mem0 ships a programmatic API. OB1 ships **MCP-first** with a community `skills/` directory of plain-text skill packs (Auto-Capture, Competitive Analysis, Deal Memo, Aiception/self-improving) that compose at the agent layer. It is more agentic in shape but the agency lives in the skills, not in the memory engine.

Net: OB1 is the **DIY, single-user, MCP-first, opinionated-stack** version of Mem0. Mem0 is the **vendor-friendly, multi-actor, library-embeddable, model-agnostic** version of OB1.

### Risks worth flagging

The ergonomics depend on every AI tool implementing remote MCP correctly; Codex needs `startup_timeout_sec = 30`; ChatGPT needs Developer Mode (which silently disables ChatGPT's own memory); Claude Desktop needs a header workaround that the server itself patches in. The metadata extraction is "best-effort" by the README's own admission, so structured filtering (`type`, `topics`) is noisier than the embeddings. And the FSL-1.1-MIT license is non-compete for two years — a vendor cannot ship OB1 as a hosted product until it converts to MIT.
