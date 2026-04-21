# Resume Instructions — Synthius-Mem Scientific Investigation

**Paused:** 2026-04-21 ~12:15 UTC
**Reason:** Anthropic API rate limit reached (resets 07:00 America/Los_Angeles).
**Resumable:** Yes — ledger is the single source of truth; no in-flight state to reconstruct.

## Current state

| Wave | Status | Notes |
|---|---|---|
| 0 Catalog | ✅ DONE | 116 canonical gaps in `ledger/GAPS.md` |
| 1 Schemas | ✅ DONE | 18 theories T-001..T-018 promoted; 7 refuted; 4 revision-needed |
| 2 Storage + CategoryRAG | ⏸ PAUSED | 21 hypotheses H-030..H-050 DESIGNED; experiments E-030..E-050 NOT YET RUN (runners hit rate limit) |
| 3 Algorithms | pending | — |
| 4 Ops + Cost | pending | — |
| 5 Security + Privacy | pending | — |
| 6 Integration + MT | pending | — |
| 7 Long-tail cleanup | pending | — |
| Final synthesis | pending | — |

## How to resume

After the rate limit resets, tell Claude:

> **"Resume the Synthius-Mem investigation from Wave 2 — re-dispatch the runners."**

Claude will:

1. Read `ledger/WAVES.md` + `ledger/HYPOTHESES.md` + `ledger/EXPERIMENTS.md` to see exact state.
2. Re-dispatch the 3 Wave 2 Runners (artifact-construction, paper-forensic, external-evidence) with the same prompts used before — the experiment specs E-030..E-050 are already designed and immutable.
3. Continue pipeline: Peer Reviewer → Adjudicator → Wave 3 → ... → Final Synthesizer.

No hypotheses or experiments are lost. Re-dispatch is safe because EXPERIMENTS.md rows still show `(pending) | (pending)` for E-030..E-050.

## Files to inspect if you want to look at progress

- `00-EXECUTIVE-SUMMARY.md` — will be produced at the very end (not yet).
- `ledger/THEORIES.md` — 18 promoted Wave 1 theories (architectural findings ready to use).
- `ledger/REFUTED.md` — 7 refutations with lessons learned.
- `ledger/HYPOTHESES.md` — all 50 hypotheses (29 Wave 1 + 21 Wave 2).
- `ledger/EXPERIMENTS.md` — 50 experiment specs.
- `ledger/TRACE.jsonl` — full event log (~150 lines so far).
- `evidence/E-001..E-029.md` — Wave 1 evidence files.

## Cost / budget state

- Wave 0 end: ~156K sub-agent tokens
- Wave 1 end: ~1.2M sub-agent tokens cumulative (rough; Wave 1 = 9 subagent calls averaging ~130K each)
- Wave 2 hypothesis + design stages: +~180K additional
- Wave 2 runners: failed — 0 additional productive tokens spent, some rate-limit-hit tokens wasted
- **Ceiling reminder (from design spec):** pause-and-confirm at 2M tokens before Wave 4 ends, 5M tokens total.
