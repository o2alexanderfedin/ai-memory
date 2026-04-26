# Claude Code Memory Systems — Survey

**Status:** active
**Started:** 2026-04-25
**Owner:** alex_fedin
**Trigger:** Research #1 — apples-to-apples comparison of Claude Code memory systems vs. this repo's approach.

## What's in this directory

| File / dir | Role | Producer |
|---|---|---|
| `BRIEF.md` | Original research charter — verbatim user request + scope | (seeded by main thread) |
| `PLAN.md` | Work breakdown, comparison schema, agent assignments | coordinator agent |
| `DIMENSIONS.md` | Apples-to-apples comparison axes (rows = subjects, cols = aspects) | coordinator agent |
| `briefs/` | One brief per research subject — input for researcher agents | coordinator agent |
| `findings/` | One findings doc per subject — output of researcher agents | researcher agents |
| `DRAFT-REPORT.md` | Synthesizer's working draft of the final report | synthesizer agent |
| `REVIEW-N.md` | Reviewer feedback per round | reviewer agent |
| `FINAL-REPORT.md` | Promoted draft once review converges | synthesizer agent |
| `STATE.md` | Live status of each artifact, updated by main thread | main thread |

## Workflow

1. **Coordinator** (one-shot): reads `BRIEF.md` → writes `PLAN.md`, `DIMENSIONS.md`, `briefs/<NN>-<subject>.md`.
2. **Researchers** (parallel, one per subject): each reads its brief and `DIMENSIONS.md` → writes `findings/<NN>-<subject>.md` and (if useful) clones the upstream into `3rd-party/<subject>/` per the parent directory's convention.
3. **Synthesizer + Reviewer** (sequential pair-loop, capped at 3 rounds): synthesizer reads all `findings/*` → writes `DRAFT-REPORT.md`; reviewer reads it → writes `REVIEW-<N>.md`; loop until reviewer reports convergence; promote to `FINAL-REPORT.md`.

All inter-agent communication is file-based — agents return only terse status to the orchestrator, never full content.

## Cross-references

- Parent directory convention: [`../../README.md`](../../README.md)
- Research subjects index: [`../../INDEX.md`](../../INDEX.md)
- Per-subject quick notes: `../<subject>.md` (alongside this dir)
