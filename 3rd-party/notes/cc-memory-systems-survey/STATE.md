# STATE — Claude Code Memory Systems Survey

**Updated by:** main-thread orchestrator (not by agents)
**Last updated:** 2026-04-25 17:42 — survey complete, FINAL-REPORT promoted

## Phase status

| Phase | Owner | Status | Output |
|---|---|---|---|
| 1. Charter | main thread | ✅ done | `BRIEF.md`, `README.md` |
| 2. Coordination | coordinator agent | ✅ done | `PLAN.md`, `DIMENSIONS.md`, `briefs/01..09` |
| 3. Research (parallel) | researcher agents (×9) | ✅ done | `findings/01..09-*.md` |
| 4. Synthesis ↔ Review loop | synthesizer + reviewer | ✅ done (converged at round 2) | `DRAFT-REPORT.md`, `REVIEW-1.md`, `REVIEW-2.md` |
| 5. Promotion | main thread | ✅ done | `FINAL-REPORT.md` |

## Subject status

| # | Subject | Findings | Per-subject note | Clone | INDEX row |
|---|---|---|---|---|---|
| 01 | native-claude-code | ✅ | ✅ | n/a (vendor docs) | ✅ |
| 02 | huryn-system | ✅ | ✅ | not cloned (no public repo) | ✅ |
| 03 | memsearch | ✅ | ✅ | ✅ `3rd-party/memsearch/` | ✅ |
| 04 | mempalace | ✅ | ✅ | ✅ `3rd-party/mempalace/` | ✅ |
| 05 | karpathy-llm-wiki | ✅ | ✅ | ✅ `3rd-party/karpathy-llm-wiki/` | ✅ |
| 06 | recall-it | ✅ | ✅ | n/a (SaaS) | ✅ |
| 07 | mem0 | ✅ | ✅ | ✅ `3rd-party/mem0/` | ✅ |
| 08 | openbrain | ✅ | ✅ | ✅ `3rd-party/openbrain/` (resolved repo: NateBJones-Projects/OB1) | ✅ |
| 09 | ai-memory-host | ✅ | ✅ | n/a (this repo) | ✅ |

## Review rounds

| Round | Verdict | File | Notes |
|---|---|---|---|
| 1 | revise | `REVIEW-1.md` | 6 actionable items (3 blocking, 3 polish); no fabrications |
| 2 | converged | `REVIEW-2.md` | 5 of 6 fully fixed, 1 partially (length: 3,622 vs 3,500 cap, overage load-bearing); no regressions |

## Final word counts

- `FINAL-REPORT.md`: 3,641 words
- 9 findings: ≤ 800 words each
- 9 per-subject notes: ≤ 200 words each

## Definition-of-done check (per BRIEF.md)

- [x] `FINAL-REPORT.md` exists, reviewer-approved (converged at round 2)
- [x] Every subject has a `findings/<NN>-<subject>.md`
- [x] Every subject registered in `../../INDEX.md` (9 rows added)
- [x] `STATE.md` reflects all artifacts (this file)
