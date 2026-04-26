# karpathy-llm-wiki

**Upstream:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
**Pinned revision:** `ac46de1ad27f92b28ac95459c782c07f6b8c964a` (2026-04-04, single revision; gist has no further history at survey time)
**Permalink:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/ac46de1ad27f92b28ac95459c782c07f6b8c964a
**Local clone:** `/Users/alexanderfedin/Projects/ai-memory/3rd-party/karpathy-llm-wiki/` (single file: `llm-wiki.md`)

## What it is

A ~75-line idea file by Andrej Karpathy. No code. The pattern: an LLM agent (Claude Code, Codex, OpenCode/Pi) maintains a personal wiki for you. Three layers — `raw/` (immutable user-curated sources), the wiki (LLM-authored markdown pages, one per entity/concept), and a schema doc (`CLAUDE.md` / `AGENTS.md`) that encodes ingest/query/lint workflows. Two special files: `index.md` (content catalogue, primary recall entry point) and `log.md` (chronological append-only journal). The wiki is just a git repo of markdown.

## Why care

Karpathy explicitly frames this as the alternative to RAG: knowledge is *compiled into a compounding artifact*, not re-derived per query. Same conceptual stratum as Huryn (Level 2 in the Simon Scrapes taxonomy) but artifact-centric rather than prompt-centric.

## Re-read pointers

- Section "Operations" (ingest/query/lint workflow).
- Section "Indexing and logging" — the ~hundreds-of-pages comfort ceiling.
- Closing "Note" — the gist is doctrine; specifics are left to your agent.
