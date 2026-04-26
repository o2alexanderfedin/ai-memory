# BRIEF — Claude Code Memory Systems Survey

**Date:** 2026-04-25 · **Trigger:** User research request "Research #1"

## Source

YouTube video: **"Every Claude Code Memory System Compared (So You Don't Have To)"**
by Simon Scrapes, 2026-04-23 — frames a six-level taxonomy of Claude Code
memory systems and links to specific implementations.

```
Timestamps from the video
00:00 - Intro: The 6 Levels of Claude Code Memory
01:37 - Level 1: What Ships With Claude Code Natively
06:31 - Level 2: Forcing Reliable Memory Recall
16:55 - Level 3: Search by Meaning, Not Just Keywords
23:45 - Level 4: Recall Verbatim Conversations
28:46 - Level 5: Build a Self-Organizing Knowledge Base
35:13 - Level 6: A Single Brain For ALL Your AI Tools
```

## Subjects in scope

| # | Subject | Source / URL (truncated as in video description) | Level (per video) |
|---|---|---|---|
| 01 | Native Claude Code memory | (built-in: CLAUDE.md, `/memory`, project memory) | 1 |
| 02 | John & Paweł's system | https://www.youngleaders.tech/p/how-i... · https://substack.com/@huryn | 2 |
| 03 | Memsearch | https://github.com/zilliztech/memsearch | 3 |
| 04 | MemPalace | https://github.com/MemPalace/mempalace | 5 |
| 05 | LLM Wiki (Karpathy) | https://gist.github.com/karpathy/442a... | 2 (or 4) |
| 06 | Recall.it | https://www.recall.it/ | 4 |
| 07 | Mem0 | https://mem0.ai/ | 6 |
| 08 | OpenBrain | https://github.com/NateBJones-Project... | 6 |
| 09 | This repo (`ai-memory`) | the repository this directory belongs to (`/Users/alexanderfedin/Projects/ai-memory`) | — |

## Deliverables

1. **Apples-to-apples comparison table** with consistent dimensions across all subjects.
2. **Performance numbers** wherever publicly documented (latency, recall@k, storage cost, token overhead, etc.). Mark as `unknown` rather than guessing.
3. **Applicability areas** — for each subject, when to choose it.
4. **Integration points** —
   a) how each plugs into agentic AI (Claude Code, MCP, agent SDK),
   b) how subjects integrate with each other (compose vs. compete vs. supersede).
5. **Useful background** — anything else that helps the user understand the landscape (taxonomies, evolution, common failure modes, open questions).

## Constraints (from the user)

- **Use a few specialized agents** to discuss/research/brainstorm.
- **Coordinator agent** facilitates discussions and plans the work stages.
- **Synthesizer + Reviewer pair** work in a loop on the final report (pair-programming style).
- **All discussions/research/brainstorming → tracked in files**, not held in main-thread context.
- **Cloning encouraged** for any subject where source code or docs are best read locally. Clones live at `3rd-party/<subject-name>/` per the parent directory's convention (gitignored). Hosted SaaS without source (Mem0, Recall.it) → research via public docs/blog/SDK.

## Definition of done

- `FINAL-REPORT.md` exists, reviewer-approved.
- Every subject has a `findings/<NN>-<subject>.md`.
- Every subject is registered in `../../INDEX.md` (parent INDEX) — even if not cloned (status `notes-only`).
- This research's row in `STATE.md` shows all artifacts produced.
