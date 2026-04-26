# Review 1 — Claude Code Memory Systems Survey (Draft)

## Round 1 verdict

**revise (issues listed)** — 7/10 checklist items pass cleanly; 3 require fixes the synthesizer can address in one round (length budget, internal numeric inconsistencies, citations completeness). No fabricated facts in the spot-checked sample; structure matches BRIEF deliverables; taxonomy and self-positioning are handled with rigor. Bloat is the dominant issue.

## Summary

The draft is factually faithful to the underlying findings — five spot-checks all trace cleanly. Coverage of BRIEF.md deliverables is complete; per-subject capsules sit comfortably under the 100-word cap (avg ~77 words). The taxonomy revisit, self-positioning on subject 09, and Mem0/OpenBrain Level-6 differentiation are well executed. The blockers are (a) a 4,505-word body against a 2,000–3,500-word target with concrete fat to cut, (b) two internal numeric inconsistencies (OpenBrain $0.10 vs $0.30; "5 of 9 — six actually" math correction left in), and (c) a small citation orphan set. None require re-research; all are editorial.

## Findings — by checklist item

1. **Coverage** — pass. Comparison table, performance table, applicability (segmented by use case), integration-into-agents and integration-between-subjects (composability matrix), and useful background (eras + failure modes + open questions) are all present. No BRIEF.md deliverable is missing.
2. **Apples-to-apples** — pass with one small caveat. Units are consistent across rows (ms, tokens, $/mo, R@k); `unknown` is preserved rather than papered over. The one fuzzy column is `setup_complexity` — Mem0 row reads "2 (SDK), 1 (SaaS)" while OpenBrain reads "3" without the same SDK/SaaS bifurcation. Not wrong, but the two systems' setup numbers are not strictly comparable. Flag in a footnote.
3. **Source-backed** — pass. Every numeric claim I sampled traces back to its finding. See spot-check log below. The "Comparability caveats" subsection under the performance table is unusually disciplined — names exactly which numbers are *Mem0-vs-Mem0*, which are retrieval recall vs end-to-end QA, which are inherited targets vs measured.
4. **Taxonomy fidelity** — pass. The 6-level scheme is reproduced; Levels 4 and 5 are explicitly flagged as disputed with reasons (Recall.it ≠ verbatim chat; "self-organizing" = structured ingest, not autonomous clustering). Subject 09 correctly sits orthogonal with `video_level = n/a`.
5. **Cross-subject claims** — mostly pass, partially aspirational. The composability matrix is honest about its limits ("Read this matrix loosely — most 'competes' entries are within a level…"). However, the cell `04 MemPalace → 07 Mem0 = competes` is well-grounded (the BENCHMARKS.md retraction story is the load-bearing data point). Many `composes-with` cells rest on "any MCP server can sit alongside CLAUDE.md" — that universal claim is correctly noted, but the matrix would be more useful if it visually distinguished documented integrations from inferred ones (asterisk vs plain).
6. **Self-positioning bias** — pass. Subject 09 is treated conservatively. The capsule explicitly says "It is not a Claude Code memory system today"; performance row marks the 21.79 ms claim as "architectural target only, not a measured number"; F3 anti-pattern correctly lists "Claude-Code-specific scratchpad workflows (no integration today)". This matches finding 09's intent.
7. **Length budget (overall)** — fail. 4,505 words against a 2,000–3,500 target — ~1,000 words over even the upper bound. The bloat is **fat, not muscle**, and is concentrated in three sections:
   - **Comparability caveats** (under Performance numbers): worthwhile but verbose; could be a 4-bullet list (~80 words) instead of 6 expanded bullets (~180 words).
   - **Open issues / `unknown` cells in the matrix**: the "Performance row is dominated by unknown..." paragraph re-states what is visually obvious from the table itself. Cut to one sentence: "7 of 9 publish no write latency; 6 of 9 no recall accuracy; 7 of 9 no scale ceiling; 6 of 9 no token-overhead figure." Saves ~120 words.
   - **PLAN R1–R7 status**: each R-bullet is a paragraph; could be one line each. Saves ~150 words.
   - **Open research questions** under Useful background: the 4 questions overlap heavily with the "Common failure modes" list above them. Cut "What's the right unit?" (already in the matrix) and trim "Single brain — federated state…" (already in OpenBrain capsule). Saves ~120 words.
   Total recoverable: ~570 words, lands the report at ~3,900–4,000. To hit 3,500 cleanly the synthesizer must additionally collapse the per-subject capsules into one paragraph each (currently 75–95 words; target 50–60).
8. **Length budget per section** — pass on capsules (average 77 words, under 100). Fail on Open issues + Useful background combined (currently ~700 words; PLAN does not budget this section but it is disproportionate to its information density).
9. **Open issues completeness** — pass. Every PLAN R1–R7 risk has a status line. R1 partial / R6 partial are honestly labeled; R2/R3/R5/R7 marked resolved. The "Items still open" sub-section names four concrete Round-2 follow-ups.
10. **Citations completeness** — fail (minor). Two URL references in the body do not appear in the Citations section:
    - Body references `https://mcp.mem0.ai/mcp` (Mem0 capsule and Integration Points table); Citations §07 lists `https://github.com/mem0ai/mem0`, `https://mem0.ai/pricing`, `https://mem0.ai/research`, `https://docs.mem0.ai`, arXiv:2504.19413, but not the MCP URL.
    - Body references `https://backend.getrecall.ai/mcp/` (Recall.it capsule and Integration Points table); Citations §06 lists `https://docs.recall.it/developer/mcp` but not the actual MCP endpoint URL.
    - Body references `qmd` (Karpathy section); Citations §05 lists `https://github.com/tobi/qmd` — correct, no orphan.
    Add the two missing URLs. Also: Citations §03 lists `(local clone)` paths but not the upstream `https://github.com/zilliztech/memsearch` URL that is implicitly referenced in the section header — already covered in finding 03's evidence_links but worth duplicating in the report's own Citations.

## Spot-check log

| # | Claim text (paraphrased) | Source finding | Verdict |
|---|---|---|---|
| 1 | "MemPalace posts 96.6% R@5 on LongMemEval (raw, no LLM)" | finding 04, C3 row: `96.6%@LongMemEval-R@5 (raw, no LLM, full 500q)` | verified ✅ |
| 2 | "Mem0: 91.6 LoCoMo / 93.4 LongMemEval / 64.1 BEAM-1M / 48.6 BEAM-10M (v3, Apr 2026)" | finding 07, C3 row: same numbers verbatim | verified ✅ |
| 3 | "Native CC: system ≈ 4,200, MEMORY.md ≈ 680, user CLAUDE.md ≈ 320, project CLAUDE.md ≈ 1,800 ('illustrative')" | finding 01, C5 row: same figures, same illustrative caveat | verified ✅ |
| 4 | "OpenBrain ~$0.10–$0.30/mo" | finding 08, C6 row: `~$0.10–$0.30/month operating cost (Supabase free tier + ~$5 OpenRouter credits 'lasts months')` | verified ✅ but inconsistent in draft — TL;DR uses "~$0.10/mo", applicability section uses "~$0.30/mo", performance table uses the range. Pick one form (the range, "~$0.10–$0.30/mo") and use it throughout. ⚠️ |
| 5 | "Memsearch 0.776 R@5 zh / 0.814 R@5 en (bge-m3 ONNX int8 internal benchmark, 955 chunks × 2172 queries)" | finding 03, C3 row: identical numbers, identical methodology line | verified ✅ |

No fabricated or distorted numbers detected in the sample. The single ⚠️ is internal inconsistency within the draft, not vs. the source.

## Required revisions for round 2

Prioritized — top three are blocking; below are polish.

1. **Cut ~600 words to land within 3,500.** Specific targets (in priority order):
   - Trim "Comparability caveats" to a 4-bullet list (~80 words; currently ~180).
   - Replace the Open Issues "`unknown` cells" paragraph with the one-sentence summary in checklist item 7. Saves ~120 words.
   - Compress PLAN R1–R7 status to one line each (no paragraph form). Saves ~150 words.
   - Cut "What's the right unit?" and trim "Single brain — federated state…" under Open research questions; both are already covered upstream. Saves ~120 words.
2. **Fix internal numeric inconsistency on OpenBrain cost.** TL;DR says "~$0.10/mo", applicability says "~$0.30/mo", performance table says the range. Use the range "~$0.10–$0.30/mo" consistently in all three places.
3. **Add missing citations.** Append `https://mcp.mem0.ai/mcp` to Citations §07 and `https://backend.getrecall.ai/mcp/` to Citations §06.
4. **Fix self-acknowledged math error in Open Issues.** The line "Recall accuracy unknown for 5 of 9 (01, 02, 05, 06, 08, 09 — six actually)" reads as an unedited correction. Just write "6 of 9" and list the six subjects cleanly.
5. **Mark inferred composability cells.** In the composability matrix, distinguish documented integrations from inferred-by-MCP-coexistence claims. Asterisk-and-footnote is the lightest fix: "* inferred from universal MCP-MCP compatibility, not from a documented integration."
6. **Reconcile setup_complexity comparability.** Add a footnote under the comparison matrix: "Mem0's `2 (SDK) / 1 (SaaS)` and OpenBrain's `3` are measured against different deliverables — Mem0 = pip install + key, OpenBrain = Supabase project + 6 SQL blocks + Edge Function deploy. Cross-row comparison is approximate."
7. **Optional polish:** Per-subject capsules average 77 words, under cap; if hitting 3,500 strictly is required, shrink each to 50–60 words. Otherwise leave alone.

## Things that are good

- "Comparability caveats" subsection — exactly the kind of self-skeptical disclosure a reader needs to interpret the recall numbers responsibly. Keep it; just shorten it.
- Subject 09 treatment is rigorous and refreshing — the report explicitly refuses to count the host repo as a Claude Code memory system today, and labels its 21.79 ms as a target rather than a measurement.
- The MemPalace-vs-Mem0 differentiator is the load-bearing analytical move of the report, and it lands. The "raw verbatim text vs. LLM-extracted facts" framing is sharp.
- Recall.it Level-4 dispute is handled openly — the report flags the source-video error rather than smuggling around it, and points at the likely conflation with recall.ai.
- The "four eras" framing (Markdown → Hybrid retrieval → Graph/typed-schema → Agentic) is a useful tax synthesis the underlying findings did not name explicitly. Worth keeping.
