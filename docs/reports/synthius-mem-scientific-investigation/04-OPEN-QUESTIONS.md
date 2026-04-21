# Open Questions — Author Q&A List

> The 11 hypotheses that reached REVISION_NEEDED terminal state — blocked on author Q&A or cross-model real-API probes — are summarized here in priority order. Each entry: (a) what the question is, (b) why it matters architecturally, (c) what evidence would close it, (d) priority rank.
>
> Cumulative totals: 149 hypotheses → 126 promoted + 18 refuted + 11 revision-needed + 0 revision-exhausted. Zero hypotheses are dead on arrival; all 11 are answerable via focused Q&A or a small probe.

---

## Priority 1 — Blocks headline-number reproducibility

### Q1. H-055 — What is the extraction LLM, and is it the same model family as answer + judge?

- **Question.** §4.1 names GPT-4.1-mini for *answer* and *judge*. The *extraction* model is never named. Is it also GPT-4.1-mini? A heavier peer (GPT-5.4 / Claude-3.5 / open-source)?
- **Why it matters.** Extraction owns the accuracy budget (94.37% rides on it). App. A.1's 5,040 tok/msg is arithmetically self-consistent with GPT-4.1-mini (∼$0.40/M input) but compatible with several OpenAI-family models; a heavier extractor would change both the cost model and the reproducibility ceiling.
- **What closes it.** (a) Author names the model + version + decoding params, OR (b) a source-code peek reveals the model ID, OR (c) a cross-model probe that reproduces 94.37% ± 1 pp on a LoCoMo subset with GPT-4.1-mini vs candidate alternatives.
- **Architecturally.** If the extractor turns out to be Claude or a local Llama, T-074 (model-gateway mitigation) becomes mandatory rather than optional, and several same-family-judge-bias arguments (T-083) shift. DIR-3.6 / DIR-3.8 depend directly on this answer.

### Q2. H-054 — What tokenizer does the budget assume?

- **Question.** Chunking (2000 / 200) and App. A.1 token budgets (2K retrieved / 1K answer system / 1.1K planner) are sized for which tokenizer? cl100k_base (OpenAI GPT-4-family)? Tiktoken o200k_base? Gemini SentencePiece? LLaMA BPE? A heuristic word counter?
- **Why it matters.** A budget of 1,100 "tokens" in one tokenizer is 1,400 in another. DIR-3.2 commits to cl100k_base by default; if the authors used a different tokenizer, chunk boundaries and budget numbers shift by up to ~20%.
- **What closes it.** Author confirmation of the tokenizer used, or a source-code peek. Linked to H-055 — if extraction is non-OpenAI, the tokenizer likely differs.
- **Architecturally.** DIR-3.2 window size adjusts; App. A.1 budget arithmetic re-validates; otherwise low architectural blast radius.

### Q3. H-060 — What structured-output mechanism is used?

- **Question.** OpenAI `response_format: json_schema` with `strict: true`? Function calling? Pydantic + retry? Grammar-constrained decoding (outlines / llguidance / xgrammar)? Anthropic tool-use?
- **Why it matters.** Strict-JSON-schema mode makes schema violations impossible by construction, explaining the paper's silence on malformed-JSON handling (G-033). If the actual mechanism is Pydantic-retry or free-form JSON parsing, the extraction failure policy (DIR-3.9) changes materially — retry loops become frequent rather than rare.
- **What closes it.** Author confirmation, or a source-code peek revealing the API call shape. Downstream: each of the six domain schemas must be verified to contain only features supported by the chosen mechanism (strict mode disallows some constructs OpenAI Pydantic/function-calling allows).
- **Architecturally.** DIR-3.8 defaults to OpenAI strict mode pending this answer.

### Q4. H-110 — Does a cross-family judge re-run preserve the 94.37% headline?

- **Question.** Does a LoCoMo re-run with a cross-family judge (e.g., Claude-3.5-Haiku or Gemini-Flash judging both Synthius-Mem and Full-Context outputs symmetrically) preserve 94.37% ± 1 pp, or does the gap collapse to <3 pp?
- **Why it matters.** This is the experimental closure for T-083 (judge-family asymmetry — the MOST architecturally consequential finding of the investigation). Zheng 2023 Table 3 documents 10–20 pp same-family self-preference bias for GPT-4 family; Synthius-Mem judges itself. The paper's +8.91 pp attribution to "architectural advantage" may reduce to 0–3 pp under symmetric judging.
- **What closes it.** A cross-family real-API red-team: Synthius-Mem output + Full-Context output + Embedding-RAG output, all judged by three independent models (Claude / Gemini / GPT). Publish per-model and averaged scores.
- **Architecturally.** If the gap collapses to 0–3 pp, the "architectural advantage" narrative requires re-scoping to "comparable accuracy with 5× token efficiency"; if it preserves, the pattern is genuinely superior. Either way, DIR-9.4 adversarial-scope honesty still applies.

---

## Priority 2 — Blocks variance analysis and evaluation confidence

### Q5. H-113 — What are the run-to-run confidence intervals at T=0?

- **Question.** Paper reports point estimates only (94.37% / 99.55% / 98.64%). What are seed-to-seed variance bands at T=0 across multiple LoCoMo runs?
- **Why it matters.** Binary-judge LLM-as-judge has known variance even at T=0 (GPU float non-determinism). At n=1,813 LoCoMo questions, sampling variance alone is sqrt(p(1-p)/n) = 0.56 pp; model variance adds 1–2 pp. Reported 94.37% should be 94.37 ± 1.5 pp at T=0, wider if T>0. Without CIs, the 8.91 pp gap (already reduced to 0–3 pp by T-083) may be within noise.
- **What closes it.** 5–10 seeded re-runs with explicit decoding parameters; publish mean ± SD per metric.
- **Architecturally.** Affects production SLO design — DIR-8.2 SLI 8 (planner-routing-accuracy) and SLI 11 (judge-agreement-rate) need variance bands to set meaningful thresholds.

### Q6–Q7. H-017 & H-044/H-045 — What are the intensity/strength scales, and what is the ranking order?

- **Question (H-017).** Is Experience.intensity a 0–1 float (H-016/T-011), or PANAS 1–5 Likert (H-017), or something else per domain?
- **Question (H-044 / H-045).** Within a domain's matching-record set, is result ranking (recency DESC, confidence DESC, stable ASC) — H-044 — or (confidence DESC, recency DESC, stable ASC) — H-045?
- **Why it matters.** Two bounded-impact questions. If scales are framework-native (PANAS 1–5 etc.), collapsing to 0–1 loses information; extraction prompts must preserve scale fidelity per domain. Ranking order affects which facts survive the 2K-token cap (DIR-5.5) — confidence-primary favors high-confidence older facts; recency-primary favors recent facts regardless of confidence.
- **What closes it.** Author publishes schema + ranking function, or source-code peek.
- **Architecturally.** DIR-1.7 defaults to 0–1 unified (T-011); DIR-5.5 defaults to (recency DESC, confidence DESC, fact_id ASC) via T-026. Both are defensible defaults under paper silence but need author confirmation for committable SLOs.

---

## Priority 3 — Blocks persona-ID commitment and schema-openness semantics

### Q8–Q9. H-022 & H-023 — Is `personaId` a UUIDv4 or a ULID, and is Style a feature dict or a prompt fragment?

- **Question.** Paper silent on both. UUIDv4 (random) or ULID (time-sortable) for persona_id? Feature dict (T-006) or prose fingerprint (T-007) for Style?
- **Why it matters.** ULID's time-sortable property aids diff-engine rollback and per-persona traversal ordering in multi-tenant stores (T-114 composite PK already declares `persona_id ULID` in DIR-2.1 — this commitment survives only if the authors don't use a non-time-sortable ID). Style form determines injection token count (feature dict ~100 tok vs prose ~200–400 tok).
- **What closes it.** External evidence (Synthius.ai repo / blog / job postings), or author commentary.
- **Architecturally.** DIR-2.1 declares ULID; if authors use UUIDv4, the commitment shifts but tenant-scoping logic (DIR-11.1) is unchanged. DIR-6.1 persona-footprint sizing shifts ±100 tok depending on Style form.

### Q10. H-027 — Is `additionalProperties` strictly false, or open-permissive?

- **Question.** Does extraction output reject extra fields (strict `additionalProperties: false`, T-016), or tolerate them silently (permissive)?
- **Why it matters.** Under strict mode (DIR-1.1), schema-violating extractions fail and enter the DLQ (DIR-3.9). Under permissive mode, extra fields pass through silently, introducing downstream storage and privacy uncertainty.
- **What closes it.** Source-code peek on the JSON-Schema objects passed to the extraction API, OR a paper-forensic hit on "extra fields are rejected" / "schema-complete extraction".
- **Architecturally.** DIR-1.1 / DIR-9.2 Layer A both declare strict; answer is load-bearing on the closed-schema defense.

---

## Consolidated Q&A list (for author email / author meeting)

In priority order, the 10 questions to put to the authors (condensed):

1. **Name the extraction LLM + version + decoding params + structured-output mechanism.** (H-055, H-060, H-054)
2. **Run a symmetric cross-family judge experiment and publish the gap.** (H-110)
3. **Publish seeded-run variance bands for all headline metrics at T=0.** (H-113)
4. **Publish the six JSON Schemas (Draft 2020-12) with `additionalProperties` mode declared.** (H-027; also satisfies G-001)
5. **Publish the intensity / strength / closeness / trust scales per domain, plus the ranking function.** (H-017, H-044, H-045)
6. **Publish the persona_id format and the Style representation (feature dict vs prose fragment).** (H-022, H-023)
7. Reconcile adversarial-scope framing: confirm "99.55% adversarial robustness" = FALSE-PREMISE QA only. (closes T-102 — erratum-worthy even if no new experiment runs)
8. Reconcile §4.2/§4.3 prose-vs-table mismatches. (closes T-064..T-067 — erratum-worthy)
9. Reconcile App. A.2 4.7M/9.3M vs Table 7 5,040 × N. (closes T-068 — erratum-worthy)
10. Clarify judge-family bias disclosure in §4.4. (closes T-083 — erratum-worthy)

---

## Path forward

- **Path A (author Q&A).** Answering Q1–Q10 closes ~70% of the residual uncertainty. Authors can respond in a half-day with a source-code peek for Q1–Q3 and an email thread for Q7–Q10.
- **Path B (cross-model probe).** A 2–3 day cross-family judge experiment (Q4 / H-110) independently validates or invalidates the 8.91 pp gap under symmetric judging. This is the single most-impactful empirical follow-up.
- **Path C (variance probe).** A 1-day multi-seed replication (Q5 / H-113) at T=0 gives defensible SLO thresholds. Cheap and load-bearing.

Until these are closed, the 11 open questions are the architect's explicit-assumption register — every DIR citing them (DIR-2.1 persona_id, DIR-3.2 tokenizer, DIR-3.6 extractor, DIR-3.8 structured output, DIR-5.5 ranking, DIR-6.1 Style form, DIR-9.4 adversarial-scope) should carry an "assumed per H-NNN; re-validate on author confirmation" flag in the production design doc.
