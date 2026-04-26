# Brief 05 — Karpathy "LLM Wiki" gist

- **Name:** LLM Wiki (Andrej Karpathy)
- **Slug:** `karpathy-llm-wiki`
- **Video level:** 2 (or 4, per BRIEF.md)
- **Source URLs:**
  - https://gist.github.com/karpathy/442a... (full slug to be resolved)
  - Any X/Twitter thread Karpathy linked from the gist
  - Any forks worth comparing (search "LLM Wiki" on GitHub)

## Cloning guidance

**Yes (gist clone).** A gist is a tiny git repo — clone to `3rd-party/karpathy-llm-wiki/` and **pin the revision hash** so future readers can reproduce.

```
cd /Users/alexanderfedin/Projects/ai-memory/3rd-party
git clone https://gist.github.com/karpathy/442a...  karpathy-llm-wiki
```

## Investigation steps

1. Read the gist top-to-bottom; capture the proposed pattern (a personal wiki the LLM reads/writes via tool use? a single markdown index?).
2. Pin the gist revision in your findings (gist permalink with hash).
3. Note any prompts/templates Karpathy provides — those are the operational core.
4. Triangulate the video's "Level 2 (or 4)" ambiguity: does the system rely on disciplined recall (Level 2) or verbatim conversation retrieval (Level 4)?
5. Compare to subject 02 (Huryn) — same conceptual layer, different execution?

## Output

- **Findings:** `findings/05-karpathy-llm-wiki.md` — DIMENSIONS table + ≤ 800 words.
- **Notes:** `3rd-party/notes/karpathy-llm-wiki.md` — ≤ 200 words.
- **Format:** see DIMENSIONS.md.

## INDEX.md row to add

```
| Karpathy LLM Wiki | https://gist.github.com/karpathy/442a... | <gist-revision-hash> | Claude Code Memory Systems Survey | active | 2026-04-25 | Personal wiki pattern; ambiguous level (2 or 4) |
```
