# 05 — Karpathy "LLM Wiki" (gist `442a6bf5...`)

**Subject slug:** `karpathy-llm-wiki`
**Source:** [gist.github.com/karpathy/442a6bf555914893e9891c11519de94f](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
**Pinned revision:** `ac46de1ad27f92b28ac95459c782c07f6b8c964a` (2026-04-04 16:25 UTC, single revision)
**Permalink (revision-pinned):** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/ac46de1ad27f92b28ac95459c782c07f6b8c964a

## Dimensions

| # | Dimension | Value |
|---|---|---|
| A1 | name | LLM Wiki |
| A2 | vendor_or_author | Andrej Karpathy (individual, ex-OpenAI / ex-Tesla) |
| A3 | license | unknown (gist carries no license file) |
| A4 | source_availability | docs-only (idea file; no implementation shipped) |
| A5 | video_level | 2 (primary) — see prose for the Level 4 caveat |
| A6 | maturity | experimental (single-revision idea file, ~3 weeks old at survey date) |
| B1 | storage_backend | markdown-files (a git repo of `.md` pages, plus a `raw/` source folder) |
| B2 | retrieval_mechanism | hybrid:agentic-search+keyword (LLM reads `index.md`, then drills into pages; optional `qmd` BM25/vector) |
| B3 | write_path | agentic (LLM ingests user-curated raw sources and authors all wiki pages) |
| B4 | update_model | merge (pages are revised in place; git provides versioning underneath) |
| B5 | memory_unit | file (one markdown page per entity/concept/source/summary) |
| B6 | schema_shape | semi-structured (free-prose pages plus a project schema in `CLAUDE.md`/`AGENTS.md`, optional YAML frontmatter for Dataview) |
| C1 | write_latency | unknown (depends on agent + model; "a single source might touch 10–15 wiki pages") |
| C2 | read_latency | unknown |
| C3 | recall_accuracy | unknown (no benchmark; pattern, not product) |
| C4 | scale_ceiling | "moderate scale (~100 sources, ~hundreds of pages)" before embedding-RAG infra is needed (gist §Indexing) |
| C5 | token_overhead_per_turn | unknown (depends on which pages the agent loads) |
| C6 | cost_model | self-host: storage is trivial; cost is the LLM tokens spent ingesting + maintaining |
| D1 | cc_integration | CLAUDE.md (the gist explicitly names Claude Code, Codex/AGENTS.md, OpenCode/Pi as targets) |
| D2 | other_clients | OpenAI Codex, OpenCode, Pi, any agent that reads markdown + edits files |
| D3 | protocols | none required; optional MCP via `qmd` |
| D4 | lock_in_level | low (plain markdown + git; portable across agents) |
| D5 | composability | composes-with: Obsidian, qmd, Marp, Dataview, Web Clipper; competes-with: NotebookLM, ChatGPT file-upload RAG |
| E1 | setup_complexity | 1 (drop-in: paste gist into agent, point at a folder) |
| E2 | maintenance_burden | low for the human (LLM does bookkeeping); medium for the agent (lint passes, contradictions) |
| E3 | observability | mixed: `log.md` append-only journal, git history, Obsidian graph view |
| E4 | failure_modes | Drift/contradiction across pages if "lint" passes are skipped; unbounded page growth past ~hundreds of pages without proper search; agent can silently corrupt cross-references on edits. |
| E5 | data_locality | local-only (filesystem + local git) |
| E6 | privacy_posture | Whatever the chosen agent leaks: content is sent to the agent's model on ingest/query. No built-in encryption, redaction, or multi-tenant separation. |
| F1 | best_fit | A solo knowledge worker building up a long-running, curated knowledge base (research deep-dive, book companion wiki, personal journal) on top of an agentic IDE. |
| F2 | anti_patterns | Multi-user/multi-agent production knowledge bases; environments where you cannot let an LLM freely edit dozens of files; sub-second retrieval workloads. |
| F3 | not_for | Latency-sensitive serving paths, regulated multi-tenant data, embedding-scale corpora (>>hundreds of sources). |
| F4 | evidence_links | • https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/ac46de1ad27f92b28ac95459c782c07f6b8c964a<br>• Local clone: `/Users/alexanderfedin/Projects/ai-memory/3rd-party/karpathy-llm-wiki/llm-wiki.md`<br>• https://github.com/tobi/qmd (recommended search tool)<br>• https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2 (community v2)<br>• https://github.com/Ar9av/obsidian-wiki (Obsidian implementation) |
| G1 | relation_to_host_repo | Same conceptual layer as `ai-memory`'s "memory as compounding artifact" stance — both reject pure RAG retrieval in favour of curated, evolving structure. The Karpathy gist is doctrine without code; `ai-memory` is the engineering side (schemas, tenants, eval, hooks). |
| G2 | open_questions | • What schema (`CLAUDE.md`) conventions does Karpathy actually use day-to-day? Not in the gist.<br>• Does the pattern hold past ~500 pages without dedicated retrieval?<br>• How are merge conflicts handled when two ingest sessions touch the same entity page?<br>• Any benchmark numbers (recall, drift) from real users? |

## Long-form

### What it actually is

The gist is a **single-revision idea document**, ~75 lines of prose, no code. Karpathy explicitly frames it as something to "copy paste to your own LLM Agent" — it expects an agentic IDE (Claude Code, Codex, OpenCode/Pi) to read the doc, then collaborate with the user on instantiating a wiki for a particular domain. It is doctrine, not a runnable system.

The proposed pattern is three layers:

1. **Raw sources** — user-curated, immutable inputs (web clippings, papers, transcripts, journal entries) sitting in `raw/`.
2. **The wiki** — a directory of LLM-authored markdown pages: one per entity, concept, comparison, summary; cross-linked, with a content-oriented `index.md` and a chronological `log.md`.
3. **The schema** — a `CLAUDE.md` / `AGENTS.md` that tells the agent how *this particular* wiki is organised and which workflows to run for ingest, query, and lint.

Three operations: **Ingest** (LLM reads new source → discusses → writes summary → updates 10–15 cross-referenced pages → appends to log), **Query** (LLM reads index → drills in → answers; "good answers can be filed back into the wiki"), and **Lint** (LLM health-checks for contradictions, stale claims, orphans, missing pages).

### Level 2 vs Level 4 — pinning the taxonomy

The brief flags ambiguity. I place this at **Level 2 (forced reliable recall)**, not Level 4 (verbatim conversation retrieval). Justification:

- The wiki is *not* a transcript store. Karpathy is explicit that synthesis pages, not raw conversations, are the unit of recall. "Good answers can be filed back into the wiki as new pages" — the answer is normalised into the wiki's schema before persistence; verbatim is incidental.
- The "forcing" mechanism is the schema doc plus disciplined ingest/lint workflows — exactly the Level 2 pattern (CLAUDE.md as the discipline layer) that Huryn (subject 02) also occupies.
- Retrieval is keyword/agentic-search over a small corpus, not embedding-based verbatim search over a long-tail conversation log (the Level 4 hallmark).

The Level 4 reading would be defensible only if you treat `log.md` as the primary recall surface. The gist explicitly does not — it positions `log.md` as a navigation/timeline aid, with `index.md` as the recall entry point.

### Comparison to subject 02 (Huryn)

Same conceptual stratum (Level 2, "be disciplined about CLAUDE.md as the memory layer"), different execution:

- Huryn's pattern is opinionated about the *prompt* (how the agent should reason about memory) and is delivered as a Substack write-up with concrete templates.
- Karpathy's pattern is opinionated about the *artifact* (a maintained wiki, separate raw/ vs wiki/ vs schema/) and is delivered as an abstract idea file that explicitly punts on schema specifics.
- Both compose with each other: you could implement Karpathy's three-layer architecture using Huryn-style prompt scaffolding inside the schema doc.

### Why Karpathy hedges

The gist's closing "Note" says it is "intentionally abstract." Everything is optional and modular. This is a deliberate choice — the pattern's strength is that it is composable with Obsidian, qmd, Marp, Dataview, Web Clipper, plain git, and any agent. The downside, for this survey, is that almost every Group C performance dimension is `unknown`: there is nothing to benchmark.

### Reception

Community uptake has been strong (multiple v2 gists, an "awesome-llm-wiki" list, an Obsidian-specific framework `Ar9av/obsidian-wiki`, several blog walkthroughs in April 2026), but no canonical implementation has emerged. That keeps the gist a *pattern* rather than a *system*.

### Failure modes worth flagging

- **Edit storms.** A single ingest can touch 10–15 pages. Without git discipline, the agent can silently break links or contradict itself across pages.
- **Schema drift.** The `CLAUDE.md`/`AGENTS.md` is co-evolved; without versioning that doc, behaviour shifts session over session.
- **Scale wall.** Karpathy himself calls out ~hundreds of pages as the comfort ceiling for index-only navigation. Past that, you must bolt on `qmd` or equivalent.
- **No multi-tenant story.** The pattern is single-user. Adapting to teams (mentioned as a use case) is left as an exercise — and the community v2 gist explicitly lists identity, security, concurrency as gaps.

### Word count

~720 words above the table.
