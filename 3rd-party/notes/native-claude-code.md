# Native Claude Code memory — quick note

**Subject 01** in the [Claude Code Memory Systems Survey](cc-memory-systems-survey/). Video level **1** (the baseline).

## What it is

Anthropic's built-in memory layer for Claude Code: plain-markdown files on the local filesystem, concatenated into the conversation at session start. Two subsystems:

- **CLAUDE.md files** — you author. Four scopes (managed policy → project → user → local), walked upward from cwd, more-specific overrides broader. Imports via `@path` (max 5-hop recursion). Path-scoped rules live in `.claude/rules/*.md` with YAML `paths:` frontmatter.
- **Auto memory** — Claude authors. Stored at `~/.claude/projects/<project>/memory/MEMORY.md` plus topic files. First **200 lines or 25 KB** of MEMORY.md loaded at startup; topic files read on-demand. Requires CC v2.1.59+.

## Numbers worth remembering

- CLAUDE.md size target: **<200 lines** (loaded in full, no truncation).
- MEMORY.md startup cap: **200 lines / 25 KB**.
- Import recursion: **max 5 hops**.
- Project-root CLAUDE.md **survives `/compact`** (re-injected from disk); nested CLAUDE.md does not.

## Links

- Findings: [`cc-memory-systems-survey/findings/01-native-claude-code.md`](cc-memory-systems-survey/findings/01-native-claude-code.md)
- Docs: https://code.claude.com/docs/en/memory · https://code.claude.com/docs/en/context-window · https://code.claude.com/docs/en/sub-agents#enable-persistent-memory
