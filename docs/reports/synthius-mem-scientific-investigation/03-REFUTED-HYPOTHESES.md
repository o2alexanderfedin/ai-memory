# Refuted Hypotheses (Graveyard)

> Compact summary of the 18 graveyard entries. Each row identifies what was tried, why it failed, and the reusable lesson. Full refuting evidence (experiment outputs + reviewer adjudication) lives in `ledger/REFUTED.md`.

---

## Refutation table

| HYPO | GAP | What was proposed | Why refuted (one line) | Winning sibling |
|---|---|---|---|---|
| **H-004** | G-002 | Specific 19-member Biography-category enumeration | synthius.ai's public Dostoevsky demo states "12 categories", contradicting the proposed list; SPECIFIC list refuted while structural "closed enum of 19" still holds. | (G-002 remains open on exact membership) |
| **H-006** | G-003 | Psychometrics native-facet-only schema | Subsumed by hybrid H-008 as the maximal endpoint; superset wins under the subset-redundancy rule. | T-005 |
| **H-007** | G-003 | Psychometrics flat-9-scores-only schema | Subsumed by hybrid H-008 as the minimal endpoint; reviewer R-007 flagged H-008 as architecturally most defensible synthesis. | T-005 |
| **H-014** | G-006 | Cross-domain refs as freeform strings only | Strictly subsumed by dual-field H-013 with `_ref: null`; H-013 also preserves extraction-time provenance H-014 discards. | T-010 |
| **H-015** | G-006 | Cross-domain refs as opaque-FK only | Strictly subsumed by dual-field H-013 with `_raw` empty; reviewer R-015 explicit: H-015 "adds no representational power but REMOVES the dual-field provenance." | T-010 |
| **H-021** | G-009 | Assistant modeled as Social-Circle person | Paper-silence triggers FAIL — H-020 (assistant outside Persona) is the simpler default; zero "I asked my AI about X" examples; zero schema bullet models the assistant. | T-014 |
| **H-025** | G-111 | Alias resolution as LLM-only (no deterministic stage) | Subsumed by hybrid H-024 as the Stage-1-empty degenerate case; paper-silence evidence for H-025 vs artifact-construction evidence for H-024. | T-015 |
| **H-032** | G-011 | MongoDB / DocumentDB substrate | Dominated by Postgres-JSONB on rollback semantics: cross-collection txns required for per-persona atomicity; "reversible diff engine" needs explicit WAL overlay since MongoDB lacks Postgres-style MVCC. | T-019 |
| **H-038** | G-014 | Single parametric retrieval tool with `domain` parameter | Structurally REFUTE'd: 6-tool form better matches §3.3 plural "domain-specific retrieval tools"; bare parametric form sacrifices T-001/T-012/T-016 closure invariants. | T-025 |
| **H-040** | G-015 | Top-K retrieval with K = `min(20, budget // avg)` heuristic | Dominated by per-domain quota + priority merging: undershoots small-fact domains (preferences → 1,400 tok < [1,500, 2,000] floor) and lacks atomic packing. | T-026 |
| **H-056** | G-028 | Heavy local/on-prem extractor (Llama-3-70B / Mixtral) | Zero paper hits on `Llama` / `Mixtral` / `on-prem` / `GPU` / `vLLM`; same-family stance (answer + judge = GPT-4.1-mini) + absence of on-prem vocabulary refute heavy-local prong. | (H-055 surviving sibling REVISION_NEEDED) |
| **H-067** | G-035 | Pure-LLM consolidation (no rule-based) | Three-way grammar parallel "fixed prompts / deterministic / rule-based" places consolidation in NON-LLM category; App. A.1 Table 7 has NO consolidation line item, inconsistent with H-067's ~50–100 tok/msg. | T-046 (3-stage hybrid) |
| **H-070** | G-038 | Planner as deterministic / non-LLM | synthius.ai home page explicit "Planner LLM … picks which domains matter"; paper §4.5 line 91 "1.1K planner LLM call". Two FAIL conditions triggered. | T-048 |
| **H-082** | G-048 | Psychometric scoring via feature extraction (no LLM) | §3.3 line 51 "evidence quotes" requirement is incompatible with pure feature pipelines (lexical/sentiment/LIWC → scalars only). | T-059 |
| **H-092** | G-097 | Cost-model: Table 7 is the typo, App. A.2 4.7M canonical | $7.42 USD back-solves to ≤2.96M (input-only) or 2.48M (blended) — never 4.7M; minimum blended rate for 4.7M would require $1.58/M < GPT-5.4 input price. Three independent tests converge against. | T-068 |
| **H-093** | G-098 | USD figures inherit App. A.2's 2× inflation downstream | Critical arithmetic: $7.42 back-solves to 2.48M matching Table 7-derived 2.52M within 1.79% — A.2 is the SOLE isolated error; cascade hypothesis falsified. | T-068 |
| **H-095** | G-100 | LangMem ~60 s retrieval is unsourced typo / unit confusion | Mem0 paper arXiv:2504.19413 + mem0.ai/blog + Deepak Gupta independent replication all confirm LangMem p95 ≈ 59.82 s on LoCoMo. Real published measurement, not typo. | (H-095 falsified; LangMem 60s stands) |
| **H-105** | G-092 | Cost claim is hardware-agnostic + GPT-5.4 forward-dated unreproducible | GPT-5.4 shipped Mar 5 2026; paper dated April 2026 (post-release); $2.50/M input + $15/M output matches OpenAI public pricing. Forward-dated prong falsified; hardware-agnostic prong preserved separately. | T-070 |

---

## Cross-cutting lessons learned

The 18 refutations cluster into 6 reusable methodological lessons that informed later waves and are useful to carry into any follow-on investigation:

### L1. Hybrid-schema synthesis subsumes endpoint-pair siblings (H-006, H-007, H-014, H-015, H-025, H-040)

When two sibling hypotheses are related as "minimal endpoint" vs "maximal endpoint" (or "X-only" vs "dual-X-and-Y"), a hybrid synthesis hypothesis almost always exists as a strict superset. **Lesson:** propose the superset upfront as a third hypothesis rather than co-promoting both endpoints; the more-general form wins under the subset-redundancy rule unless paper text actively forbids the second prong.

### L2. Paper-silence is weaker than artifact-construction evidence (H-021, H-025, H-070)

When two siblings have asymmetric evidence — one supported only by paper-silence, the other by artifact-construction or external-source corroboration — the stronger-evidence hypothesis subsumes even if both had SUPPORT verdicts. **Lesson:** design FAIL conditions on the paper-silence-only sibling as "paper-silence triggers FAIL" when a non-default sibling has stronger evidence; this cleanly resolves the pair without requiring separate refutation experiments.

### L3. Sibling hypotheses must not sacrifice prior-wave invariants (H-038)

Any later-wave hypothesis that can only be realized by opening `additionalProperties` (refuting T-001) or typing a field as free-form `string` (refuting T-012/T-016) is automatically refuted regardless of its other merits. **Lesson:** the closure invariants of Wave 1 are keystones; downstream waves cannot trade them away for local simplifications.

### L4. Cost-model claims require USD back-solve arithmetic against the pricing anchor (H-092, H-093, H-105)

Multi-step cost-model error analysis cannot rely on internal-consistency reading alone. **Lesson:** for any disputed cost figure, back-solve USD against the published pricing anchor and cross-reference to independently-labeled "Measured" columns (here: Table 11). Three converging tests (USD back-solve + "Measured" label + savings-ratio match) are decisive even when each test alone is plausible. Do not assume intermediate errors cascade downstream without arithmetic verification.

### L5. Compound hypotheses fail on their weakest prong (H-105)

When a hypothesis chains two sub-claims (e.g., "hardware-agnostic AND forward-dated unreproducible"), the adjudication rule is: reject the compound, promote any surviving sub-claim separately under a more specific theory. **Lesson:** for forward-dated pricing or technology claims, always verify model release date vs paper publication date before asserting unreproducibility.

### L6. External-artifact disambiguation beats paper-internal speculation (H-004, H-070, H-095, H-056)

Author-voiced external artifacts (synthius.ai homepage, GitHub, blog posts), peer-paper measurements (Mem0 benchmarks, MT-Bench), and on-prem-vocabulary forensic sweeps are decisive disambiguators when the paper itself is silent or ambiguous. **Lesson:** before promoting a competing-implementation hypothesis, validate against author-voiced external artifacts; "Synthius.ai publishes a different number" or "the home page explicitly labels Planner LLM" is dispositive in ways internal paper-forensic cannot match.

---

## What the graveyard means for the architect

Three pragmatic implications:

1. **The cost-model dispute is settled in favor of Table 7.** Architects should price at 5,040 tok/msg as the idealized floor and 6,300–8,500 tok/msg as the realistic production figure (T-073). App. A.2's 4.7M / 9.3M figures should NOT be used in CFO presentations; the paper has an isolated drafting error there.
2. **The LangMem 60-second baseline is real.** The "3000× faster than LangMem" rhetoric (21.79 ms / 60 s ≈ 2,755×) survives the forensic check (H-095 refuted). This is a defensible competitive claim, modulo the judge-family bias caveat that affects accuracy comparisons (T-083).
3. **Single-tool / single-prong realizations of CategoryRAG, consolidation, planner, and psychometric scoring are all refuted.** The architecture is necessarily multi-stage / multi-tool / hybrid, NOT a parsimonious single-LLM-call substitute. Architects who hope to simplify by collapsing stages should know that each collapse was tried and refuted with evidence.

For the 11 hypotheses that did NOT reach a terminal verdict — they remain in REVISION_NEEDED status, blocked on author Q&A or cross-model real-API probes — see `04-OPEN-QUESTIONS.md`.
