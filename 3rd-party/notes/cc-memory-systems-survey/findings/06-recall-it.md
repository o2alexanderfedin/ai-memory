# 06 — Recall.it (a.k.a. getRecall.ai)

> Hosted SaaS knowledge base ("personal second brain"). The Simon Scrapes
> video filed it under Level 4 ("recall verbatim conversations"); after
> investigation that framing is **inaccurate** — Recall does not record
> Claude Code chat turns. It stores user-curated content (articles, PDFs,
> podcasts, YouTube, notes) as "cards" and exposes them read-only to LLMs
> via an MCP server and REST API. Findings below reflect what it actually
> does; mismatches with the "verbatim recall" label are flagged in prose.

## Dimensions

| # | Dimension | Value |
|---|---|---|
| A1 | name | Recall (recall.it / getrecall.ai) |
| A2 | vendor_or_author | Recall — Paul Richards (CEO), Igor Gligorevic (CTO), Sankari Nair (COO); Amsterdam, NL |
| A3 | license | proprietary SaaS |
| A4 | source_availability | docs-only |
| A5 | video_level | 4 (per Simon Scrapes; see "Caveat on Level 4" below) |
| A6 | maturity | active (founded Nov 2022, Recall 2.0 launched Apr 2026, $1.5M seed Dec 2024) |
| B1 | storage_backend | cloud-saas (Google Cloud, europe-west1 / Belgium), local-first sync on device |
| B2 | retrieval_mechanism | hybrid:semantic+keyword (search has `focused` and `exhaustive` modes) plus structured-query (filter_by_metadata) |
| B3 | write_path | manual (browser extension, web app, mobile, bulk import); no write API yet |
| B4 | update_model | overwrite (cards are user-edited; no public version history) |
| B5 | memory_unit | other:card (a "card" is a saved item — article, PDF, podcast, YouTube, note — with optional AI summary chunks) |
| B6 | schema_shape | semi-structured (card has source URL, tags, date, content chunks) |
| C1 | write_latency | unknown |
| C2 | read_latency | unknown (Groq case study cites "10x lower cost" + "fast inference" but no ms numbers) |
| C3 | recall_accuracy | unknown |
| C4 | scale_ceiling | unknown (Plus/Max are "unlimited" subject to fair-use review) |
| C5 | token_overhead_per_turn | unknown (depends on MCP client and tool-call sizes) |
| C6 | cost_model | Free ($0, 10 AI cards/mo); Plus $10/mo yearly; Max $38/mo yearly |
| D1 | cc_integration | MCP-server (read-only; OAuth, no API key; URL `https://backend.getrecall.ai/mcp/`) |
| D2 | other_clients | cursor, claude-desktop, any MCP client; standalone web/mobile/Chrome ext |
| D3 | protocols | MCP, REST (Bearer `sk_…`, base `https://backend.getrecall.ai/api/v1`) |
| D4 | lock_in_level | low (Markdown export of full KB via Settings > Export) |
| D5 | composability | composes-with: any MCP-host (Claude Code, Claude Desktop, Cursor); standalone for ingestion |
| E1 | setup_complexity | 1 (sign up, paste MCP URL, OAuth) |
| E2 | maintenance_burden | none (vendor-managed) |
| E3 | observability | ui-dashboard (web app) — no public metrics/traces endpoint |
| E4 | failure_modes | Read-only MCP means Claude cannot persist new memories back; OAuth session expiry breaks the MCP link until re-auth. |
| E5 | data_locality | mixed (local-first device cache + vendor-cloud GCP Belgium) |
| E6 | privacy_posture | EU residency (GCP europe-west1); FAQ asserts "best-practice" security, no published encryption-at-rest specifics; multi-tenant; account delete wipes "locally and from our servers." |
| F1 | best_fit | A user who wants their own curated reading-list / research notes searchable by Claude Code via MCP, without standing up infra. |
| F2 | anti_patterns | Trying to use it as auto-recording chat memory for Claude Code — it has no write API and ingests user-saved content, not session transcripts. |
| F3 | not_for | Verbatim conversation logging; team-shared agent memory; air-gapped/regulated workloads; high-throughput programmatic ingestion. |
| F4 | evidence_links | see below |

## Caveat on Level 4 ("verbatim conversation recall")

The brief inherits the video's Level-4 label. Investigation contradicts it:

- The **MCP server exposes only four read tools** (`search`,
  `filter_by_metadata`, `get_document_content`, `explore_kb`) and the
  REST API explicitly says "currently supports read-only operations. A
  write API is on the roadmap." So Claude Code **cannot push session
  turns into Recall** today. It can only retrieve from a KB the user
  built by hand or by browser extension.
- The unit of storage is a **card** (article/PDF/podcast/note), not a
  conversation turn. Verbatim source content of saved cards is preserved
  alongside an AI summary; this is "verbatim source" not "verbatim chat."
- Likely confusion: the survey video may be conflating Recall.it
  (knowledge base) with **Recall.ai** (a different YC company at
  `recall.ai`, founded 2020 by Amanda Zhu / David Gu, ~$50M raised, that
  *does* expose meeting recordings + transcripts via API). They share
  a name and not much else.

I am keeping `video_level=4` per the brief but flagging the mismatch as
an open question for the synthesizer.

## What it actually is (≤ 800 words)

Recall is a hosted, multi-platform "second brain": a Chrome extension and
mobile/web app where users save articles, PDFs, podcasts, YouTube,
TikToks, books, recipes, Wikipedia, and free-form notes. Each saved
item becomes a **card** with an AI-generated summary, smart tags, and
"connections" to related cards (knowledge-graph style). Power-user
features include spaced-repetition quizzes, multi-voice TTS playback of
summaries, and "augmented browsing" that resurfaces related cards as you
read on the open web. The marketing claim is "trusted by 500,000+
professionals" with logos for LinkedIn, NYU, Stanford, Bloomberg.

**Architecture as visible from the docs.** Cards live in a Google Cloud
database in `europe-west1` (Belgium), with a local-first device cache
that syncs to the cloud. The retrieval surface is a small REST API
(`/cards`, `/cards/{id}`, `/search`) authenticated with `sk_…` bearer
tokens, and an MCP server at `https://backend.getrecall.ai/mcp/`
authenticated by browser-OAuth (scope `kb:read`). Both surfaces are
read-only. Search supports `focused` (5–10 cards) and `exhaustive`
(10–25 cards) modes, plus a metadata-only filter and a KB overview
("explore_kb"). Per the Groq customer story, inference for summaries
and search ranking moved from another provider to Groq for "10x lower
cost"; concrete latency or recall numbers are not published.

**Pricing.** Free tier ($0) limits AI summaries to 10/mo but allows
unlimited manual saves and full API/MCP access. Plus is $10/mo billed
yearly; Max is $38/mo billed yearly with frontier-model access and 1:1
onboarding. "Unlimited" tiers carry an explicit fair-use clause —
Recall reserves the right to throttle abusers.

**Claude Code fit.** You install the MCP server URL into a Claude-Code/
Cursor/Claude-Desktop config, OAuth once in the browser, and Claude can
then `search` your cards or pull a card's full text on demand. There is
**no write path** today, so it is not a long-term agent memory in the
sense of the rest of this survey — it is a *retrieval-augmented
reference library that happens to live in your browser too*. Vendor
lock-in is low because Settings > Export produces a zipped Markdown
dump of the whole KB.

**Privacy posture.** EU residency (GCP Belgium) is a plus for European
users. Encryption specifics are not in the FAQ — the FAQ defers to a
privacy policy. Account deletion is supposed to wipe both device-local
and server data and is irreversible. Subscription cancellation does
**not** revoke KB access, which is friendly. Multi-tenant by default.

**Maturity.** Founded November 2022 from a Hacker News post titled
"A tool to help you remember shit you are interested in." Seed round
$1.5M closed Dec 2024 (Jason Calacanis lead). Recall 2.0 announced
14 Apr 2026 — the version that introduced the MCP server. So MCP/CC
integration is roughly **two weeks old as of this survey** (today is
2026-04-25).

**Why the Level-4 label is shaky.** Verbatim *chat* recall would
require ingesting Claude Code session turns. Recall has neither a write
API nor a CC hook nor a session-recorder; it ingests user-curated
*source documents*. It is closer to the Pocket/Readwise lineage with an
MCP face bolted on. If the survey wants a real "Level 4 verbatim
conversation recall" subject, candidates surfaced during this research
are `claude-echoes` (pgvector + Ollama, every turn captured) or
`recallmcp.com` (Redis-backed cross-session memory) — both unrelated
to recall.it.

## Evidence

- https://www.recall.it/ — landing, 500k user claim, multi-model chat
- https://www.recall.it/pricing — Free / Plus / Max tiers
- https://www.recall.it/faq — GCP Belgium residency, deletion, export
- https://www.recall.it/blog — post list (Recall 2.0 dated 14 Apr 2026)
- https://docs.recall.it/ — docs index (Developer → MCP, API)
- https://docs.recall.it/developer/mcp — `kb:read` scope, four read tools
- https://docs.recall.it/developer/api — read-only REST, `sk_…` keys
- https://www.prnewswire.com/news-releases/from-a-hacker-news-post-to-1-5m-funding-recall-is-on-a-mission-to-bring-order-to-content-chaos-302318912.html — funding & founders
- https://siliconcanals.com/recall-bags-1-4m-funding/ — Amsterdam HQ
- https://groq.com/customer-stories/why-recall-switched-to-groq-fast-intelligent-knowledge-retrieval-10x-lower-cost — inference backend
- https://www.ycombinator.com/companies/recall-ai — *different* company, called out for disambiguation

## G — Survey-specific notes

| # | Dimension | Value |
|---|---|---|
| G1 | relation_to_host_repo | The host `ai-memory` repo aims at first-party agent memory (write + read, multi-tenant, local-controlled). Recall.it is an *external read-only knowledge source* — not a competitor for agent memory, but composable as a retrieval tool that an `ai-memory`-backed agent could call via MCP. |
| G2 | open_questions | • Is the Simon Scrapes video really referring to recall.it, or to recall.ai (meeting transcripts)? Likely conflated. <br>• Encryption-at-rest specifics (FAQ defers to privacy policy not fetched here). <br>• Real read latency numbers — no published figure. <br>• Write-API ETA — "coming soon" only. <br>• Token cost of an exhaustive search call into a Claude Code context. |
