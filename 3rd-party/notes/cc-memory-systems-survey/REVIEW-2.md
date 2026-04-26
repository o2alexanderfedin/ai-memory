# Review 2 — Claude Code Memory Systems Survey (Round 2)

## Round 2 verdict

**converged** — every REVIEW-1 required revision is addressed (5 fully fixed, 1 partially fixed by design — the 122-word overage is load-bearing not fat). No regressions detected. ≤ 2 minor remaining issues, both already self-flagged in the draft's "Items still open" section.

## Delta against REVIEW-1

| # | Original complaint | Round-2 status | Where in DRAFT-REPORT | Note |
|---|---|---|---|---|
| 1 | Cut ~600 words to land within 3,500 (target trims: Comparability caveats, `unknown` paragraph, PLAN R1–R7 status, Open research questions) | ⚠️ partially fixed | Changelog line 14; §Comparability caveats lines 76–80 (now 4 bullets); §`unknown` cells line 193 (one sentence); §PLAN R1–R7 lines 205–211 (one line each); §Open research questions lines 184–187 (cut from 4 to 2) | All four named trims executed correctly. Final = 3,622 words (122 over upper bound, –20% from 4,505). The overage is load-bearing — every remaining sentence either carries a benchmark number, a citation hook, or a comparability caveat the reviewer's spot-checks already endorsed. Treating per PLAN context-note as ⚠️ but not a blocker. |
| 2 | Internal inconsistency on OpenBrain cost ($0.10 vs $0.30 vs range) | ✅ fixed | TL;DR line 18 ("~$0.10–$0.30/mo"); Applicability line 102 (same); Performance table line 73 (same) | All three sites now use the range form. |
| 3 | Add missing citations (`mcp.mem0.ai/mcp`, `backend.getrecall.ai/mcp/`) | ✅ fixed | Citations §06 line 268 (`backend.getrecall.ai/mcp/`); Citations §07 line 279 (`mcp.mem0.ai/mcp`) | Both URLs present. |
| 4 | Self-acknowledged math note "5 of 9 — six actually" | ✅ fixed | §Open issues line 193 — clean "6 of 9 (01, 02, 05, 06, 08, 09)" with the six subjects listed | Reads as polished output, no editorial residue. |
| 5 | Mark inferred composability cells with asterisk + footnote | ✅ fixed | §Composability matrix lines 132–144; legend on line 144 ("`*` = inferred from universal MCP–MCP compatibility, not a documented integration") | Asterisks applied across MCP-coexistence cells (e.g., 01→06, 02→all, 04→01, 06→01, 09→01). Footnote present and accurate. |
| 6 | Reconcile setup_complexity comparability with footnote | ✅ fixed | §Comparison matrix line 38 ("Setup-complexity caveat: Mem0's `2/1` and OpenBrain's `3` measure different deliverables…") | Footnote placed directly under the matrix as recommended; phrasing matches REVIEW-1's suggested text. |

## Spot-check log (round 2)

Three new numeric claims, traced to findings (different from REVIEW-1's five):

| # | Claim text (paraphrased) | Source finding | Verdict |
|---|---|---|---|
| 1 | "MemPalace 88.9% R@10 LoCoMo / 92.9% ConvoMem / 80.3% R@5 MemBench" (performance table line 69) | finding 04, C3 row: `88.9%@LoCoMo-R@10 (hybrid_v5, top-10); 92.9%@ConvoMem-recall; 80.3%@MemBench-R@5` | verified ✅ — exact numerical match, methodology preserved (hybrid_v5, top-10) |
| 2 | "Mem0 ~7.0K LoCoMo / ~6.8K LongMemEval retrieval payload (>90% vs. 25K full)" (performance table line 72) | finding 07, C5 row: `~7.0K tokens mean retrieval payload (LoCoMo); ~6.8K (LongMemEval) — README v3 table; >90% reduction vs full-context (~25K)` | verified ✅ — exact match including the >90%/25K framing |
| 3 | "Subject 09: 21.79 ms architectural target only, ~750 µs probe budget; 200K rows warm-cache budget; 2000/k per-domain quota (DIR-5.5)" (performance table line 74) | finding 09 — C2 row: `21.79 ms@arch-target-mean … warm-cache budget breakdown estimates ~750 µs probe`; C4 row: `200K rows@arch-budget`; C5 row: `DIR-5.5 specifies a 2000/k per-domain quota` | verified ✅ — all four quantities trace cleanly; "architectural target only" framing preserved per PLAN R5 |

No fabricated numbers. The synthesizer's restraint in marking 21.79 ms as "architectural target only, not measured" continues to honor PLAN R5.

## Regressions

none. Specifically checked:

- The trimmed Comparability caveats subsection (now 4 bullets) retains all four load-bearing caveats from round 1 (Mem0-vs-Mem0, MemPalace recall-vs-QA, Subject 09 inherited target, Recall.it pricing-vs-latency). Nothing dropped.
- The compressed PLAN R1–R7 status (one-line each) preserved every R-label and resolution status (R1 partial, R2 resolved, R3 resolved, R4 as-expected, R5 resolved, R6 partial, R7 resolved). No status drift.
- Cutting "What's the right unit?" and "Single brain — federated state" from Open research questions did not orphan any citation — both removed items were prose-only with no unique URLs.
- Per-subject capsules trimmed to ~55 words still preserve the load-bearing "gotcha" for each subject (compaction loss, MEMORY.md cap, model download hang, HNSW bloat, ingest discipline, write-API-absence, v3 break, FSL non-compete, no-CC-integration). All gotchas survived.
- Asterisk footnote on the composability matrix (item 5) added without disturbing the load-bearing **MemPalace vs Mem0 = competes** call (line 140, bolded, no asterisk) — that one is documented, not inferred.

## Convergence justification

PLAN §3 specifies `converged` when every REVIEW-1 item is fixed (≥ 5 of 6) AND no regressions AND ≤ 2 minor remaining issues. Round 2 shows 5 of 6 fully fixed (items 2, 3, 4, 5, 6) and 1 partially fixed (item 1: word count at 3,622 vs 3,500 cap, +122 words / +3.5% overage). Per the synth's own changelog and my independent reading of the trimmed sections, the overage is load-bearing — the named trims were all executed and further cuts would drop benchmark specifics that REVIEW-1's spot-checks confirmed as load-bearing. No regressions detected across the five regression vectors I checked. Remaining open items (MemPalace 19-vs-29 tool count; Mem0 hosted ADD-only status; Recall.it write-API ETA; Subject 09 measured-vs-target latency) are all already disclosed in §"Items still open" and depend on upstream signal that won't materialize in another review round. Promote.
