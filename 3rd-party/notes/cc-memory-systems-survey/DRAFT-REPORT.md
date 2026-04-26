# Claude Code Memory Systems — Comparative Survey (Draft)

## Changelog

- **Round 1 (2026-04-25)** — initial draft, 4,505 words.
- **Round 2 (2026-04-25)** — addressed REVIEW-1 items:
  - Item 1: Cut ~600 words across Comparability caveats (collapsed to 4-bullet list), Open Issues `unknown` paragraph (reduced to one sentence), PLAN R1–R7 status (one line each), and Open research questions (dropped two redundant items).
  - Item 2: OpenBrain cost made consistent — uses `~$0.10–$0.30/mo` in TL;DR, applicability, and performance table.
  - Item 3: Added `https://mcp.mem0.ai/mcp` to Citations §07 and `https://backend.getrecall.ai/mcp/` to Citations §06.
  - Item 4: Replaced self-acknowledged math note with clean "6 of 9" listing the six subjects.
  - Item 5: Added asterisk-and-footnote convention to composability matrix marking inferred MCP-coexistence cells.
  - Item 6: Added `setup_complexity` comparability footnote under the comparison matrix.
  - Item 7 (optional polish): Partially applied — capsules trimmed to ~55 words each; verbose intros across Applicability, Useful Background, Open Issues, and TL;DR also tightened.
  - Word count after revisions: 3,622 (down from 4,505; -20%). Slightly above the 3,500 upper bound by ~120 words; further trimming risks dropping cited specifics (benchmark numbers, finding-traceable detail) that the reviewer's spot-checks confirmed as load-bearing.

## TL;DR

Nine "Claude Code memory" systems span three real architectures and one identity confusion. **Native CLAUDE.md** (1) and **Huryn/Conneely** (2) are markdown-only — zero infra, low recall, solo-dev fit. **Memsearch** (3) and **MemPalace** (4) add hybrid vector + BM25; MemPalace posts the best published recall (96.6% R@5 LongMemEval) by *refusing* to summarize. **Karpathy's LLM Wiki** (5) is doctrine, not a runtime. **Recall.it** (6) is a curated reading-list SaaS mislabeled in the source video — no write API for chat turns. **Mem0** (7) and **OpenBrain** (8) both target Level 6; Mem0 is a multi-actor SDK with 91.6@LoCoMo, OpenBrain a single-user MCP server self-deployed on Supabase for ~$0.10–$0.30/mo. **Subject 09** (`ai-hive-memory`, host repo) is an embedding-free typed-schema backend with no Claude Code surface today; in scope by problem domain, not integration.

## Comparison matrix

9 curated columns; the full 32-dimension table per subject lives in `findings/<NN>-*.md`.

| # | Subject | Lvl | License | Storage | Retrieval | Write path | CC integration | Setup | Best-fit (one-line) |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Native CC memory | 1 | proprietary | markdown files | full-text + agentic file-read | manual + agentic auto-memory | native | 1 | Repo-shared coding standards |
| 02 | Huryn / Conneely | 2 | unknown | markdown files | keyword (named files) | agentic append | CLAUDE.md + opt PreToolUse hook | 1–2 | Solo dev project notes, zero infra |
| 03 | Memsearch | 3 | MIT | markdown + Milvus | hybrid dense + BM25 + RRF | auto-extracted (Stop hook) | hooks + skill (no MCP) | 1 | Cross-CLI semantic recall |
| 04 | MemPalace | 5 | MIT | ChromaDB + SQLite KG | hybrid semantic + BM25 + opt LLM rerank | CLI + Stop/PreCompact hooks | MCP + hooks + slash-cmds + CLI | 2 | Local-first verbatim memory |
| 05 | Karpathy LLM Wiki | 2 (4-disputed) | unknown (gist) | markdown files | agentic + keyword | agentic (LLM authors) | CLAUDE.md / AGENTS.md | 1 | Solo curated wiki |
| 06 | Recall.it | 4 (disputed) | proprietary SaaS | cloud-SaaS | hybrid semantic + structured | manual (no write API) | MCP read-only | 1 | LLM-searchable reading list |
| 07 | Mem0 | 6 | Apache-2.0 / SaaS | SQLite + 20+ vector stores | hybrid semantic + BM25 + entity | auto-extracted (LLM facts) | MCP + hooks + skill | 2 (SDK), 1 (SaaS) | Production per-user memory |
| 08 | OpenBrain (OB1) | 6 | FSL-1.1-MIT | Postgres + pgvector | hybrid semantic + JSONB | manual + LLM metadata | remote MCP | 3 | Solo DIY single-brain |
| 09 | `ai-hive-memory` (host) | n/a | unknown | Postgres JSONB + GIN | structured-query (no embeddings) | auto-extracted (planned) | none today | 4 | Typed per-persona backend |

> Full per-subject tables (all 32 dimensions, with citations) live in `findings/01-native-claude-code.md` … `findings/09-ai-memory-host.md`.

> **Setup-complexity caveat:** Mem0's `2/1` and OpenBrain's `3` measure different deliverables — Mem0 = `pip install` + key; OpenBrain = Supabase project + 6 SQL blocks + Edge Function deploy. Cross-row comparison is approximate.

## Per-subject capsule

**01 — Native Claude Code memory.** The Level-1 baseline: plain markdown loaded once per session. CLAUDE.md is human-authored, MEMORY.md Claude-authored (v2.1.59+). Hierarchy: managed → project → user → local. **Gotcha:** nested CLAUDE.md is *not* re-injected after `/compact` until a matching file is read again — source of most "instruction disappeared" reports.

**02 — Huryn / Conneely.** Two-author pattern (Huryn seeded, Conneely extended). CLAUDE.md tells Claude to append discoveries (`date — what — why`) to `.claude/memory.md`, plus a routing block. Conneely adds a PreToolUse Python hook (~80 ms first / ~5 ms after) injecting per-project memory once per PPID. **Gotcha:** routing rules in `MEMORY.md` get silently truncated by Anthropic's 200-line cap.

**03 — Memsearch (Zilliz).** MIT, Milvus-backed semantic memory layer. Markdown daily logs (source of truth) plus a Milvus collection with dense + BM25 fields fused via RRF. Default embedding is local ONNX bge-m3 int8 (558 MB, no API key). Pure-hook integration (no MCP); recall delegated to a forked subagent skill. **Gotcha:** first run hangs while the model downloads.

**04 — MemPalace.** Local-first counterargument to LLM-extracted memory. Conversation stored verbatim in 800-char "drawers" inside a wing/room/drawer/closet hierarchy on ChromaDB + temporal-KG SQLite. Hybrid retrieval (vector + BM25 + closet pre-pass + opt LLM re-rank). Strongest published recall in the survey: 96.6% R@5 LongMemEval, *no LLM in the hot path*. **Gotcha:** ChromaDB HNSW can bloat (issue #346 fixed a 441 GB case).

**05 — Karpathy LLM Wiki.** Single-revision gist (~75 lines, no code). Doctrine for an agentic IDE to maintain a curated markdown wiki: `raw/` sources → LLM-authored entity/concept pages → schema in `CLAUDE.md`/`AGENTS.md`. Three ops: ingest, query, lint. Karpathy caps comfort at "~hundreds of pages" before bolting on `qmd`. **Gotcha:** ingests touch 10–15 pages; without git discipline the agent breaks links.

**06 — Recall.it.** Hosted multi-platform "second brain" — Chrome extension + mobile/web app where users save articles, PDFs, podcasts, YouTube. Each item becomes a "card" with AI summary. Read-only MCP (`backend.getrecall.ai/mcp/`, four tools) and read-only REST. **Gotcha — taxonomy correction:** source video labels this Level 4 ("verbatim conversation recall") but there is *no write API*. Likely conflated with `recall.ai` (a different YC company doing meeting recordings).

**07 — Mem0.** Apache-2.0 OSS SDK plus YC-funded SaaS. Pluggable across 20+ vector stores; default Qdrant + SQLite. LLM-extracted facts (`gpt-5-mini`, `ADDITIVE_EXTRACTION_PROMPT`), hybrid retrieval with entity boost. **April 2026 v3 break:** ADD-only single-pass extraction; graph memory removed (was Neo4j/Memgraph/Kuzu). Official CC plugin (MCP + 5 hooks + skill); broadest editor matrix in the survey.

**08 — OpenBrain (OB1).** Single-user, MCP-first stack: Supabase + pgvector + OpenRouter, ~400 LOC Deno in one Edge Function exposing 4 MCP tools. Single shared access key. Append + dedup via SHA-256; no semantic update step. Multi-tool federation works because every MCP client points at the same URL. **Gotcha:** FSL-1.1-MIT forbids competing hosted use for two years; Codex needs `startup_timeout_sec = 30`.

**09 — `ai-hive-memory` (host repo).** Python 3.12 FastAPI service persisting persona facts into six closed Pydantic schemas (biography, experiences, preferences, social_circle, work, psychometrics) on Postgres JSONB + GIN. **Embedding-free** by Decision 1 — typed equality/range/`in`. Multi-tenancy via RLS. **Not a Claude Code memory system today:** no CLAUDE.md, no MCP server code, no slash-command; MCP is a roadmap deployment variant. In scope by problem-domain proximity only.

## Performance numbers

Every published numeric claim, consistent units, `unknown` preserved.

| # | Subject | Write latency | Read latency | Recall accuracy | Scale ceiling | Token overhead / turn | Cost (mo) |
|---|---|---|---|---|---|---|---|
| 01 | Native CC | unknown | unknown | unknown | CLAUDE.md < 200 lines; MEMORY.md cap **200 lines / 25 KB**; `@`-imports depth 5; skills 5K each / 25K total | per-session: system ≈ **4,200**, MEMORY.md ≈ **680**, user CLAUDE.md ≈ **320**, project ≈ **1,800** (illustrative) | bundled with CC sub |
| 02 | Huryn / Conneely | unknown | hook **~80 ms first / ~5 ms after** | unknown ("24 self-written rules by week 3") | inherits 200-line MEMORY.md cap | unknown | $0 infra |
| 03 | Memsearch | unknown | unknown | **0.776 R@5 zh / 0.814 R@5 en** (bge-m3 ONNX int8, 955 chunks × 2172 queries) | unknown (Milvus Lite → Server → Cloud) | cold-start: last 30 lines × 2 daily logs | $0 self-host / pay-per-token cloud / Zilliz free tier |
| 04 | MemPalace | "Hooks < 500 ms" budget | "Startup < 100 ms" budget | **96.6% R@5** LongMemEval-raw 500q; **98.4% R@5** hybrid_v4 450q; **88.9% R@10** LoCoMo; **92.9%** ConvoMem; **80.3% R@5** MemBench | anecdotal 50K–200K drawers; HNSW fix #346 for 441 GB | ~600–900 tokens L0+L1 | $0 core; opt LLM rerank ~$0.001/q Haiku, ~$0.003/q Sonnet |
| 05 | Karpathy Wiki | unknown | unknown | unknown | "~100 sources, ~hundreds of pages" before embedding RAG | unknown | self-host; cost = LLM tokens |
| 06 | Recall.it | unknown | unknown ("10x lower cost" Groq, no ms) | unknown | "unlimited" with fair-use | unknown | $0 Free (10 cards/mo); **$10/mo Plus**; **$38/mo Max** |
| 07 | Mem0 | unknown | **0.88s p50 LoCoMo / 1.09s LongMemEval / 1.00s BEAM-1M** | **91.6 LoCoMo / 93.4 LongMemEval / 64.1 BEAM-1M / 48.6 BEAM-10M** (v3) | benchmark to BEAM-10M | **~7.0K LoCoMo / ~6.8K LongMemEval** retrieval payload (>90% vs. 25K full) | OSS free + infra; SaaS $0 Hobby / **$19 Starter** / **$249 Pro** |
| 08 | OpenBrain | unknown | unknown (cold "few seconds") | unknown | Supabase free tier 500MB / 5GB | default `limit=10`, `threshold=0.5` | **~$0.10–$0.30/mo** (Supabase free + ~$5 OpenRouter) |
| 09 | `ai-hive-memory` | unknown | **21.79 ms** *architectural target only*, ~750 µs probe budget | unknown (LoCoMo future) | **200K rows** warm-cache budget | `2000/k` per-domain quota (DIR-5.5) | self-host (Postgres + LiteLLM) |

**Comparability caveats.**
- Mem0 v3 numbers are *Mem0-vs-Mem0*; baselines are not retabulated. The "+26% over OpenAI Memory" claim comes from arXiv:2504.19413.
- MemPalace's 96.6% is *retrieval recall*, not end-to-end QA. Memsearch's recall is *internal* (own corpus, no third-party benchmark).
- Subject 09's 21.79 ms is inherited from a source paper; no benchmark file yet in repo. Native CC token figures are "illustrative" per Anthropic docs.
- Recall.it's "10x lower cost" is a pricing differential, not latency.

## Applicability — when to choose which

### Single-developer, local, code-focused

**Native CC (01)** — right for shared coding standards in a repo, build/test commands, markdown re-loaded each session. Wrong for cross-machine sync, semantic recall, compliance guarantees.

**Huryn / Conneely (02)** — right when you want native CC plus a routing pattern and will manage discipline (don't put routing in MEMORY.md). Wrong for anything beyond keyword file-name routing or shared team memory.

**Karpathy Wiki (05)** — right for a long-running curated wiki you keep adding to (research, book companion, journal). Wrong at sub-second latency, multi-tenant, or past ~hundreds of pages without `qmd`.

### Single-user, semantic, cross-CLI

**Memsearch (03)** — right when you bounce between Claude Code, Codex, OpenClaw, OpenCode and want consistent semantic recall over markdown. Wrong for typed graphs, cross-user ACLs, billion-record scale.

**MemPalace (04)** — right when you want conversations kept verbatim, fully offline, MCP-compatible, and trust the "no extraction" thesis. Wrong for multi-tenant, cloud-sync, or compliance-sensitive verbatim retention.

### Cross-tool "single brain"

**Mem0 (07)** — right for per-user memory in *production* agents across frontends, tolerating LLM-extraction non-determinism, with vendor-supported distribution. Wrong for code/file/document-RAG (unit is a fact, not a chunk), graph traversal (removed in v3), or sub-100ms writes.

**OpenBrain (08)** — right for a solo user deploying a Supabase project for ~$0.10–$0.30/mo with every MCP client sharing the same Postgres. Wrong for teams (single shared key), air-gapped environments, or hosted resale (FSL non-compete).

### Curated reading library, not chat memory

**Recall.it (06)** — right when you want saved articles/PDFs/YouTube searchable by Claude Code via MCP. Wrong as chat-memory; no write API, unit is a card, not a turn.

### Backend-service infrastructure, not Claude-Code-side

**`ai-hive-memory` (09)** — right when a host agent wants typed per-persona structured recall (biography/work/preferences/social-circle/experiences/psychometrics) with tenant isolation. Wrong for free-form notes, CC scratchpad workflows (no integration today), or similarity search over unstructured prose.

## Integration points

### a) Into agentic AI — the canonical hook per subject

| # | Subject | Canonical CC hook | Other agent surfaces |
|---|---|---|---|
| 01 | Native CC | drop a `CLAUDE.md` (or `/init`) | none (AGENTS.md cross-import is a workaround) |
| 02 | Huryn / Conneely | paste Huryn block into `claude.md`; opt. PreToolUse hook | none |
| 03 | Memsearch | install plugin → 4 lifecycle hooks + recall skill in forked subagent | OpenClaw, OpenCode, Codex CLI |
| 04 | MemPalace | `claude plugin install` → 19–29 MCP tools + Stop/PreCompact hooks + slash-cmds | Codex CLI, Gemini CLI, AnythingLLM, any MCP host |
| 05 | Karpathy Wiki | author `CLAUDE.md`/`AGENTS.md` schema per the gist | OpenAI Codex, OpenCode/Pi, any markdown-editing agent |
| 06 | Recall.it | paste `backend.getrecall.ai/mcp/` into MCP config; OAuth in browser | Cursor, Claude Desktop, any MCP client |
| 07 | Mem0 | `/plugin install mem0@mem0-plugins`; MCP `mcp.mem0.ai/mcp` (9 tools) + 5 hooks + skill | Cursor, Codex, Cowork, OpenClaw, Vercel, LangGraph, CrewAI, AutoGen, browser ext |
| 08 | OpenBrain | `claude mcp add --transport http open-brain ...` | Claude Desktop, ChatGPT (Dev Mode), Codex, Cursor/VS Code/Windsurf via supergateway |
| 09 | host repo | none today; MCP is a future deployment per `ARCHITECTURE.md` §DIR-7.5 | none today (REST shipped, gRPC + MCP planned) |

### b) Composability matrix — composes / competes / supersedes / standalone

From each finding's `D5` cell.

| ↓ from \ → to | 01 Native | 02 Huryn | 03 Memsearch | 04 MemPalace | 05 Karpathy | 06 Recall | 07 Mem0 | 08 OpenBrain | 09 Host |
|---|---|---|---|---|---|---|---|---|---|
| 01 Native | — | substrate | substrate | substrate | substrate | composes* | composes | composes | composes* |
| 02 Huryn | composes | — | composes* | composes (routing) | composes | composes* | composes* | composes* | composes* |
| 03 Memsearch | composes (hooks) | composes* | — | competes (recall) | composes* | n/a | competes | competes | composes (backend) |
| 04 MemPalace | composes (MCP)* | composes* | competes | — | composes* | n/a | **competes** | competes* | competes |
| 05 Karpathy | composes (CLAUDE.md) | composes | composes* | composes* | — | n/a | n/a | n/a | composes (doctrine) |
| 06 Recall | composes (MCP)* | composes* | n/a | n/a | n/a | — | composes* | composes* | composes (read-only source)* |
| 07 Mem0 | composes (plugin) | composes* | competes | **competes** | n/a | composes* | — | **competes** | n/a (could compose)* |
| 08 OpenBrain | composes (MCP)* | composes* | competes | competes* | n/a | composes* | **competes** | — | n/a |
| 09 Host | composes (substrate)* | composes* | composes (backend) | competes (extractor stance) | composes (doctrine) | composes (source)* | n/a | n/a | — |

`*` = inferred from universal MCP–MCP compatibility, not a documented integration.

Read loosely — most "competes" entries are within-level; most "composes" rest on universal MCP coexistence. Load-bearing dispute: **MemPalace vs. Mem0** — MemPalace's "raw verbatim text beats LLM extraction" thesis directly challenges Mem0's "LLM-extracted facts" architecture; MemPalace's 96.6% R@5 is the data point.

## The 6-level taxonomy revisited

Simon Scrapes' six levels frame the survey but don't survive contact intact:

| Level | Video framing | Survey reality |
|---|---|---|
| 1 | What ships natively | Holds. Subject 01. Markdown loaded once per session. |
| 2 | Forcing reliable recall | Holds. Subjects 02 (Huryn) and 05 (Karpathy) — prompt scaffolding vs. wiki schema; agentic-write vs. agentic-author. |
| 3 | Search by meaning | Holds. Subject 03 (Memsearch). |
| 4 | Recall verbatim conversations | **Disputed.** Subject 06 (Recall.it) recalls user-curated cards via read-only MCP, not conversations. Likely conflated with recall.ai. True Level-4 candidates (`claude-echoes`, `recallmcp.com`) are out of scope. |
| 5 | Self-organizing knowledge base | Mostly holds. Subject 04 (MemPalace) self-organizes via deterministic regex/heuristics, not autonomous clustering — LLM-routed indexing tanked to 34.2%, deterministic keyword routing fixed it. "Self-organizing" here = "structured ingest." |
| 6 | Single brain for ALL tools | Holds, but split: **Mem0 = library + multi-actor + many backends + LLM extraction**; **OpenBrain = remote-MCP-only + single-user + opinionated stack + append-dedup**. |

**Subject 09** sits orthogonal — backend service, not a CC surface (`video_level = n/a`, `cc_integration = none`). In scope by problem-domain, not by video level.

## Useful background

### Evolution of the field (the four eras)

1. **Markdown era** — system prompt + hand-curated files. Subjects 01, 02, 05.
2. **Hybrid retrieval era** — vector + BM25 + RRF over chunked markdown. Subjects 03, 04 (and 07/08 underneath).
3. **Graph / typed-schema era** — KGs and typed stores layered on vectors. MemPalace ships a temporal KG; Mem0 shipped graph then *removed* it in v3 (Apr 2026); the host repo is purely typed-schema, embedding-free.
4. **Agentic era** — the LLM owns read/write, picks files/skills, summarizes, prunes. Native CC auto-memory (01), Karpathy (05), Mem0 extraction (07).

### Common failure modes (cross-cutting)

- **Recall drift** — markdown systems without linting (01, 02, 05) accumulate contradictions; Karpathy mitigates via "lint" pass.
- **Compaction loss** — Native CC nested CLAUDE.md is *not* re-injected after `/compact`; inherited by anyone composing on (01).
- **Truncation traps** — Anthropic's 200-line MEMORY.md cap silently eats routing rules (Conneely's #1 lesson).
- **Index bloat** — ChromaDB HNSW grew to 441 GB in one MemPalace install (issue #346).
- **First-run model download** — Memsearch hangs while 558 MB ONNX bge-m3 downloads.
- **OAuth/key expiry** — Recall.it MCP breaks until re-auth; OpenBrain key is a single shared secret.
- **Lock-in via algorithm versioning** — Mem0 v2→v3 (Apr 2026) removed graph and broke `enable_graph` callers.
- **Cold-start latency** — OpenBrain Edge Function "few seconds" cold; Codex needs `startup_timeout_sec = 30`.
- **Non-determinism in extraction** — Mem0's LLM extraction is not turn-to-turn reproducible.

### Open research questions

- **Benchmark for "self-organizing"?** LongMemEval/LoCoMo/MemBench measure recall, not structuring quality — the same R@5 hides different organization strategies.
- **Is graph memory worth it?** Mem0's v3 retreat from graph traversal is a signal; benchmarks don't reward graph queries. MemPalace keeps a temporal KG but its load-bearing recall is from verbatim drawers, not the graph.

## Open issues

### `unknown` cells in the matrix

7 of 9 publish no write latency; 6 of 9 (01, 02, 05, 06, 08, 09) no recall accuracy; 7 of 9 no scale ceiling; 6 of 9 no token-overhead figure. Only MemPalace and Mem0 use shared external benchmarks.

### Contradictions resolved in this draft

1. **Recall.it Level-4 label** — no write API; likely conflated with recall.ai. Flagged in taxonomy revisit; `video_level=4` kept per brief with caveat.
2. **MemPalace MCP-tool count** — README says 29, plugin manifest says 19. Reported as "19–29" pending verification.
3. **Mem0 graph status** — v2 had Neo4j/Memgraph/Kuzu; v3 removed graph. Treat v3 (Apr 2026) as canonical.
4. **MemPalace v1 closet routing** — LLM-routed indexing tanked to 34.2%; deterministic keyword routing fixed it. Load-bearing argument against "Level 5 = LLM-driven."
5. **Subject 09 self-positioning** — graded conservatively per PLAN R5; not a CC memory system today (orthogonal axis).

### PLAN.md R1–R7 status

- **R1** (video taxonomy) — *partial*: Levels 4/5 ambiguities flagged in taxonomy revisit.
- **R2** (Huryn/Conneely identity) — *resolved*: both authors and lineage confirmed.
- **R3** (Karpathy gist stability) — *resolved*: pinned revision `ac46de1a…`.
- **R4** (hosted-SaaS opacity) — *as expected*: Recall.it / Mem0 SaaS numbers largely `unknown`.
- **R5** (self-positioning bias) — *resolved*: Subject 09 graded conservatively (`cc_integration = none`, `video_level = n/a`).
- **R6** (composability claims) — *partial*: matrix marks inferred MCP-coexistence cells with `*`.
- **R7** (Level 6 differentiator) — *resolved*: Mem0 vs. OpenBrain split articulated.

### Items still open

- MemPalace MCP tool count (19 vs 29).
- Whether Mem0 hosted Platform moved to ADD-only or still UPDATE/DELETEs for paid tenants.
- Recall.it write-API ETA ("coming soon", no date).
- Subject 09: 21.79 ms target vs. measured.

## Citations

Every URL referenced, deduped, grouped by subject.

### 01 — Native Claude Code memory
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/overview
- https://code.claude.com/docs/en/sub-agents#enable-persistent-memory
- https://code.claude.com/docs/en/context-window

### 02 — Huryn / Conneely
- https://www.youngleaders.tech/p/how-i-finally-sorted-my-claude-code-memory
- https://substack.com/@huryn/note/c-216337711
- https://substack.com/@huryn/note/c-228204100
- https://substack.com/@huryn/note/c-228883267
- https://www.productcompass.pm/p/claude-code-guide

### 03 — Memsearch
- https://github.com/zilliztech/memsearch
- (local clone) `3rd-party/memsearch/README.md`
- (local clone) `3rd-party/memsearch/docs/architecture.md`
- (local clone) `3rd-party/memsearch/docs/design-philosophy.md`
- (local clone) `3rd-party/memsearch/evaluation/README.md`
- (local clone) `3rd-party/memsearch/plugins/claude-code/README.md`

### 04 — MemPalace
- https://github.com/MemPalace/mempalace
- (in-repo) `benchmarks/BENCHMARKS.md`
- (in-repo) `docs/HISTORY.md`
- (in-repo) `docs/CLOSETS.md`
- (in-repo) `mempalace/{searcher.py, palace.py, knowledge_graph.py, backends/base.py}`
- (in-repo) `.claude-plugin/plugin.json`, `hooks/README.md`, `examples/mcp_setup.md`

### 05 — Karpathy LLM Wiki
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/ac46de1ad27f92b28ac95459c782c07f6b8c964a
- (local clone) `/Users/alexanderfedin/Projects/ai-memory/3rd-party/karpathy-llm-wiki/llm-wiki.md`
- https://github.com/tobi/qmd
- https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
- https://github.com/Ar9av/obsidian-wiki

### 06 — Recall.it
- https://www.recall.it/
- https://www.recall.it/pricing
- https://www.recall.it/faq
- https://www.recall.it/blog
- https://docs.recall.it/
- https://docs.recall.it/developer/mcp
- https://docs.recall.it/developer/api
- https://backend.getrecall.ai/mcp/
- https://www.prnewswire.com/news-releases/from-a-hacker-news-post-to-1-5m-funding-recall-is-on-a-mission-to-bring-order-to-content-chaos-302318912.html
- https://siliconcanals.com/recall-bags-1-4m-funding/
- https://groq.com/customer-stories/why-recall-switched-to-groq-fast-intelligent-knowledge-retrieval-10x-lower-cost
- https://www.ycombinator.com/companies/recall-ai *(disambiguation; different company)*

### 07 — Mem0
- https://github.com/mem0ai/mem0 (commit `bd9d27ff…`)
- https://mem0.ai/pricing
- https://mem0.ai/research
- https://docs.mem0.ai
- https://mcp.mem0.ai/mcp
- arXiv:2504.19413
- (local clone) `/Users/alexanderfedin/Projects/ai-memory/3rd-party/mem0`

### 08 — OpenBrain (OB1)
- https://github.com/NateBJones-Projects/OB1 (commit `7bbc37e2…`)
- (local clone) `/Users/alexanderfedin/Projects/ai-memory/3rd-party/openbrain/{server/index.ts, docs/01-getting-started.md, CLAUDE.md}`
- https://www.simplenews.ai/news/ob1-open-brain-offers-dollar010month-personal-knowledge-infrastructure-for-ai-agents-ssf5
- https://promptkit.natebjones.com/20260224_uq1_guide_main

### 09 — `ai-hive-memory` (host repo)
- `/Users/alexanderfedin/Projects/ai-memory/pyproject.toml`
- `/Users/alexanderfedin/Projects/ai-memory/docs/architecture/ARCHITECTURE.md`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/main.py`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/storage/{tables,rls,repository}.py`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/schemas/*.py`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/api/*.py`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/ingest/*.py`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/llm/gateway.py`
- `/Users/alexanderfedin/Projects/ai-memory/src/ai_hive_memory/observability/otel.py`
