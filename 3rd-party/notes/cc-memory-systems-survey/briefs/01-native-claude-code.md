# Brief 01 — Native Claude Code memory

- **Name:** Native Claude Code memory (CLAUDE.md, `/memory`, project memory, plus subagent / skills surfaces)
- **Slug:** `native-claude-code`
- **Video level:** 1
- **Source URLs:**
  - https://docs.claude.com/en/docs/claude-code/memory
  - https://docs.claude.com/en/docs/claude-code/overview
  - Anthropic's "Engineering" blog posts on Claude Code (search "Claude Code memory")
  - The user's own machine: `~/.claude/CLAUDE.md` and any project `CLAUDE.md` files (see [BRIEF.md](../BRIEF.md))

## Cloning guidance

**No.** Claude Code is closed-source. Use docs + on-disk inspection of `~/.claude/` (read-only — do not exfiltrate user data).

## Investigation steps

1. Read the official docs URL above end-to-end. Capture: where each memory file lives, precedence order, slash commands (`/memory`, `/init`), import syntax (`@path/to/file`).
2. Note the **levels** Anthropic itself ships: enterprise, user-global, project, project-local, and any `imports`. Map each to DIMENSIONS.md cells.
3. Capture token-budget behavior: when does CLAUDE.md content enter the context window, and how is its size accounted for?
4. Record interaction with sub-agents and skills (do they inherit CLAUDE.md?).
5. Compare against the YouTube video's "Level 1" framing — does the doc match what the video describes?

## Output

- **Findings:** `findings/01-native-claude-code.md` — table per DIMENSIONS.md + ≤ 800 words prose.
- **Notes:** `3rd-party/notes/native-claude-code.md` — ≤ 200 words, links to findings + key doc URLs.
- **Format:** see DIMENSIONS.md (lead with the dimension table).

## INDEX.md row to add

```
| Native Claude Code memory | https://docs.claude.com/en/docs/claude-code/memory | n/a (vendor docs) | Claude Code Memory Systems Survey | notes-only | 2026-04-25 | Built-in CLAUDE.md system, Level 1 |
```
