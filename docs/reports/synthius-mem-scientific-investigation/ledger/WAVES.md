# Waves Dashboard

Live status of the scientific investigation. Updated by Coordinator after each wave.

| Wave | Theme | Status | Gap-IDs | Gaps | Hypotheses | Promoted | Refuted | Rev-Exhausted | In Progress |
|:---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 0 | Gap Catalog | ✅ DONE | G-001..G-116 | 116 | — | — | — | — | — |
| 1 | Schemas | ✅ DONE | G-001..G-010, G-111, G-113, G-116 | 13 | 29 | 18 | 7 | 0 | 0 |
| 2 | Storage + CategoryRAG | ✅ DONE | G-011..G-017, G-019, G-054, G-107 | 10 | 21 | 16 | 3 | 0 | 0 |
| 3 | Algorithms (extract/plan/consolidate/answer/psychometric) | ✅ DONE | G-021..G-050 (+related) | 28 | 35 | 28 | 4 | 0 | 0 |
| 4 | Ops + Cost Model + Eval Reproducibility (+ numerical inconsistencies) | ✅ DONE | G-032, G-051, G-063..G-070, G-082..G-105, G-109, G-114, G-115, G-036, G-093..G-100 | 39 | 40 | 34 | 4 | 0 | 0 |
| 5 | Security + Privacy + Threat Model | ✅ DONE | G-026, G-052, G-053, G-055..G-062, G-080, G-081, G-110 | 14 | 17 | 17 | 0 | 0 | 0 |
| 6 | Integration Contract + Multi-tenancy | PENDING | G-018, G-072..G-079, G-106, G-108, G-112 | 11 | — | — | — | — | — |
| 7 | Long-tail MINOR/NIT cleanup | PENDING | (any remaining MINOR/NIT not resolved by group-in-wave) | variable | — | — | — | — | — |

**Total gaps in wave scope:** 115 (one gap — G-020 concurrency — moves to Wave 2 with storage siblings).

**Last updated:** 2026-04-21 — Wave 3 complete. 28 theories promoted (T-035..T-062), 4 refuted (H-056, H-067, H-070, H-082), 3 revision-needed (H-054, H-055, H-060) carried forward as open questions blocked on Synthius source-code / author Q&A. Cumulative: 62 theories promoted (T-001..T-062), 14 refuted, 9 revision-needed. Zero hypotheses rev-exhausted. Wave 3 HIGH-confidence theories: T-042 (6 concurrent extraction calls), T-044 (per-fact WAL diff engine), T-046 (3-stage hybrid consolidation), T-048 (GPT-4.1-mini planner — externally confirmed), T-055 (dual-layer refusal gate).

**Wave 4 complete (2026-04-22):** 34 theories promoted (T-063..T-096), 4 refuted (H-092 cost-model loser, H-093 USD cascade, H-095 LangMem-60s-is-real, H-105 forward-dated-pricing compound), 2 revision-needed (H-110 same-LLM-bias probe, H-113 CI-variance probe — both re-run in later waves with cross-family real-API probes). H-118 adjudicated as single narrowed theory T-089 (mis-citation + missing-ref) per Adjudicator directive, avoiding H-118a/b split. Cumulative: 96 theories promoted (T-001..T-096), 18 refuted, 11 revision-needed. Zero hypotheses rev-exhausted. Wave 4 HIGH-confidence theories: T-064–T-067 (prose-number typo cluster, three independent tables), T-068 (Table 7 canonical cost model — three-way converging tests), T-072 (embarrassingly-parallel per-persona scaling), T-073 (realistic production cost breakdown 6,300-8,500 tok/msg), T-075 (batch-only current pipeline), T-083 (judge-family bias reduces architecture-only contribution to 0-3 pp — MOST ARCHITECTURALLY CONSEQUENTIAL finding of the investigation), T-085 (per-participant isolation), T-086 (pass@1), T-088 (9-BLOCKER infra-only reproduction infeasibility), T-090 (F1 vs binary-judge metrics-category error), T-096 (20W brain rhetorical-only).

**Wave 5 complete (2026-04-23):** 17 theories promoted (T-097..T-113), 0 refuted, 0 revision-needed. All 17 H-126..H-141 PASS on internal runner; all 17 SUPPORT on peer review with confidence calibration (9 HIGH, 8 MEDIUM). Cumulative: 113 theories promoted (T-001..T-113), 18 refuted, 11 revision-needed. Zero hypotheses rev-exhausted. Wave 5 HIGH-confidence theories: T-098 (STRIDE 3-boundary irreducibility proof), T-100 (H-128b 2-stage prompt-injection defense, externally verified OWASP + Prompt-Guard-86M + Llama-Guard + NeMo Guardrails), **T-102 (adversarial-scope relabel — 99.55% is FALSE-PREMISE QA only; 4 of 5 NIST AI RMF / OWASP LLM Top 10 axes untested; KEY forensic finding materially affecting architectural-honesty framing and compounding T-083 judge-family bias)**, T-103 (OpenTelemetry + 12 SLIs + Grafana CNCF-standard), T-104 (per-stage retry/DLQ + WAL replay + persona-bounded blast radius, composed from T-018/T-032/T-033), T-105 (Presidio Apache-2 pre-extraction scrubber, ≥40 PII types, 5-30ms latency), T-107 (cross-persona attribute-as-claim-to-owner + consent-token structural enforcement), T-109 (GDPR Art. 17 two-tier soft-delete + NIST SP 800-88 Rev. 1 §4.7 crypto-shredding), T-110 (envelope encryption + TLS 1.3 + regional-KMS pinning), T-111 (T-009 additive provenance extension with injection_risk + pii_tokens_redacted). Sibling pairs carried: T-104↔T-113 (recovery variance regime) and T-109↔T-112 (erasure retention regime); T-109 is GDPR-first default. T-099 (H-128a) MEDIUM-confidence-flagged for cross-model real-API red-team follow-up (same single-instance-probe caveat pattern as R-017/R-027/R-057/R-069/R-081/R-110). T-101/T-106/T-108 moderate-invention (synthesized thresholds/allowlist/residency matrix) → MEDIUM.

## Cost envelope tracking

| Checkpoint | Cumulative sub-agent tokens |
|---|---:|
| Wave 0 end | 156,833 |
| Ceiling trigger | 2,000,000 before Wave 4 end; 5,000,000 total |
