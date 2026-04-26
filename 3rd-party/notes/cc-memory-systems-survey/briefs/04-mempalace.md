# Brief 04 — MemPalace

- **Name:** MemPalace
- **Slug:** `mempalace`
- **Video level:** 5 ("Build a self-organizing knowledge base")
- **Source URLs:**
  - https://github.com/MemPalace/mempalace
  - Any blog/landing page linked from the repo

## Cloning guidance

**Yes.** Clone to `3rd-party/mempalace/`. Pin the commit.

```
cd /Users/alexanderfedin/Projects/ai-memory/3rd-party
git clone https://github.com/MemPalace/mempalace.git mempalace
```

## Investigation steps

1. README + any `ARCHITECTURE.md` / `docs/` in the clone. Identify the "self-organizing" mechanism — agentic clustering? LLM-driven taxonomy? Graph + summarization loops?
2. Storage: graph DB? Vector + relational? Markdown filesystem with cross-links?
3. How does it integrate with Claude Code (MCP, slash command, external CLI)?
4. Capture cadence: does reorganization run synchronously per-write, or batch / scheduled?
5. Look for cost/perf claims in the repo.
6. License + maturity signals.

## Output

- **Findings:** `findings/04-mempalace.md` — DIMENSIONS table + ≤ 800 words.
- **Notes:** `3rd-party/notes/mempalace.md` — ≤ 200 words.
- **Format:** see DIMENSIONS.md.

## INDEX.md row to add

```
| MemPalace | https://github.com/MemPalace/mempalace | <commit-hash> | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 5 — self-organizing knowledge base |
```
