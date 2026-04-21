# Promoted Theories — Compact Catalog

> 126 theories derived from 149 hypotheses across 7 waves. Full evidence chains and refuted-sibling cross-references live in `ledger/THEORIES.md`; this file is the navigable index grouped by architectural layer. Format: `T-NNN | confidence | one-line statement`.

**Confidence legend:** HIGH (multiple converging SUPPORTs) / MEDIUM (single SUPPORT, no contradicting evidence) / LOW (supported but narrowly; carry as product option).

---

## 1. Schemas & Data Model (T-001..T-018, T-039, T-045)

Persona domain schemas, cross-domain references, confidence + provenance envelope, typed decomposition. Anchored by the keystone theory T-001 (closed JSON Schema Draft 2020-12) + T-034 (embedding-free).

| ID | Conf | Statement |
|---|---|---|
| T-001 | HIGH | Six domains representable as closed JSON Schema Draft 2020-12 objects with `additionalProperties:false`, typed primitives, closed enums; no union-over-primitive-vs-object; no "Other" escape. |
| T-002 | HIGH | Each schema shaped as two-layer `{persona_id, schema_version, facts:[FactItem]}` envelope; hierarchical Experiences via `parent_event_id` FK + `children` array in the flat facts array. |
| T-003 | HIGH | Six schemas share a single `$defs.CommonEnvelope` block — bundled form ~27% smaller than inline-envelope; no paper-cited behavior conflicts with any envelope field. |
| T-004 | MEDIUM | The 19 Biography categories are empirical (LoCoMo-indexed), not inherited from McAdams / Luhmann / SRRS / SSA. |
| T-005 | HIGH | Psychometrics = hybrid `{framework:{trait:{score, evidence_quote, confidence, facets?}}}`; validates both minimal 9-trait and maximal NEO-PI-R-facet endpoints. Subsumes the two earlier endpoint siblings. |
| T-006 | MEDIUM | Style = small structured feature dictionary (~10 scalar fields) rendered verbatim into the answer LLM's "Writing style:" section at ~100–130 tokens. |
| T-007 | MEDIUM | Style-as-prose-fingerprint-prompt-fragment is an architecturally-valid sibling under paper silence; composable with T-006. |
| T-008 | MEDIUM | All six domains normalize confidence to `number (0..1)`; "high/medium/low" is a display function over numeric bins. Psychometric 0–100 trait scores are a distinct axis. |
| T-009 | MEDIUM | Shared `provenance:{source_message_id, source_chunk_id, extracted_at, extractor_version}` on all six domains — jointly forced by T-044 rollback + GDPR Art. 17 erasure. |
| T-010 | HIGH | Cross-domain references use dual-field `{_raw, _ref}`; strictly supersedes freeform-only (H-014 REFUTED) and opaque-FK-only (H-015 REFUTED). |
| T-011 | MEDIUM | Intensity/strength/closeness/trust all normalized to `number (0..1)`; emotions = closed Plutchik-8 + neutral enum. |
| T-012 | HIGH | Facts stored decomposed into typed sub-fields; dates ISO-8601 + explicit `precision: year\|month\|day`. Required for 21.79 ms field-level matching. |
| T-013 | MEDIUM | Dual-storage (composite string + typed fields overlay) is a valid sibling realization; ~2× overhead negligible at 500 MB scale. |
| T-014 | HIGH | The assistant's identity is OUTSIDE the Persona model — not a peer Persona, not a Social-Circle person. Six-domain store represents user only. |
| T-015 | HIGH | Alias resolution is two-stage: deterministic case-fold + nickname-table → LLM adjudication on ambiguity. Cross-persona alias resolution out of scope. |
| T-016 | HIGH | "Structured" = closed JSON Schema + `additionalProperties:false` + NO referential integrity at storage layer (FK resolution is a consolidation-time concern). |
| T-017 | HIGH | "Hierarchical" Experiences = event part-of decomposition (DAG, usually tree), NOT is-a taxonomy. |
| T-018 | HIGH | "Hierarchical" carries three distinct meanings: Experiences-as-tree / recursive summarization / consolidation restructuring. Each requires a distinct implementation. |
| T-039 | MEDIUM | Relevance threshold = per-fact LLM score 0–1 emitted by extraction LLM; deterministic filter at 0.5; 57.66% peripheral-suppression is the observed post-filter rate. |
| T-045 | MEDIUM | Schema evolution = `schema_version` + lazy migration on read. Minor-version bump for new category with default-valued new fields; $925K re-extraction event (G-022) deferred. |

---

## 2. Storage & Retrieval (T-019..T-034, T-042, T-044, T-076)

Postgres-JSONB substrate, GIN+B-tree index plan, in-memory hash overlay, WAL + snapshot, CategoryRAG exact typed-field match, 6-tool function-call catalog.

| ID | Conf | Statement |
|---|---|---|
| T-019 | MEDIUM | **Postgres JSONB per-persona rows** — 6 tables `{persona_id, fact_id, schema_version, fields jsonb, envelope jsonb, created_at, updated_at}` + functional B-tree indexes on hot sub-fields. 4+ orders of magnitude headroom vs 21.79 ms. |
| T-020 | MEDIUM | **SQLite-per-persona file + global tenant index DB** sibling — most literal mapping of Fig. 1's "6 JSON files" bullet; GDPR Art. 17 = one-file-rm. |
| T-021 | MEDIUM | **In-memory per-persona hash maps** at session load — ~100–150 ns lookup; hot-path overlay atop T-019/T-020 durability + T-033 WAL. |
| T-022 | HIGH | Postgres index plan: `GIN (fields jsonb_path_ops)` + functional B-tree on hot fields. Hot-path ~750 µs (29× headroom); worst-case range ~5 ms (4× headroom). |
| T-023 | HIGH | **CategoryRAG matching primitive = exact match on typed sub-fields.** No LLM-per-query, no embeddings, no fuzzy inside the match step. 21.79 ms mean arithmetically incompatible with anything else. |
| T-024 | HIGH | Matching refinement: case-fold + NFKC + whitespace-collapse + punctuation-strip + per-domain alias-table expansion. 10/10 synthetic paraphrased-name tests. |
| T-025 | HIGH | Retrieval-tool API = one OpenAI-style function-call tool per domain (6 tools; per-domain field enums from T-001). Catalog + planner + question = ~1,080 tokens within App. A.1's 1,100-token budget. |
| T-026 | MEDIUM | 2K retrieved-context cap = per-domain quota + priority merging (2000/k per domain; sort by recency DESC, confidence DESC, fact_id ASC; atomic pack). |
| T-027 | HIGH | Paraphrase = planner-LLM query rewriting with few-shot field-name mapping table. Single planner call (no separate rewrite LLM). 10/10 synthetic paraphrases. |
| T-028 | HIGH | Complementary paraphrase: schema-level field-name aliases in JSON Schema `description`. Composes with T-027 as defense-in-depth. |
| T-029 | MEDIUM | Tail paraphrase fallback = post-retrieval LLM-judge only when primary returns empty. Admissible only if miss rate ≤ 0.108%. |
| T-030 | MEDIUM | Per-persona footprint ≤ 10 MB p75 (median ~2.5 MB); fits every proposed substrate without tiering. |
| T-031 | MEDIUM | §5.2 relevance threshold is the sizing governor — no explicit cap; 57.66% peripheral suppression is the sole size-control mechanism. |
| T-032 | HIGH | Mid-write torn state prevented by **per-persona single transaction over all 6 domains**. Native under Postgres; per-persona file IS the txn unit under SQLite. §3.3 "full rollback" grammar-compatible only with single-transaction. |
| T-033 | HIGH | **Append-only WAL + periodic snapshot** realizes §3.3 "reversible diff engine"; classic event-sourcing. |
| T-034 | HIGH | **Keystone — strictly embedding-free.** 13-keyword paper sweep: all 26+ embedding hits are baseline / competitor / critique. Zero hits attach embeddings to Synthius-Mem's own stack. |
| T-042 | HIGH | "Parallel extraction" = 6 concurrent LLM calls (one per domain). Wall-clock bounded by slowest; token cost additive matches Table 7's 5,040 tok/msg. |
| T-044 | HIGH | Diff engine primitives = `add \| edit \| delete` at per-fact granularity in persistent append-only event log; minimum-viable for §3.3's "full rollback capability". |
| T-076 | MEDIUM | Production caching overlay = per-persona LRU cache over 6 domain hot-facts; invalidation via per-persona cache-epoch counter bumped on WAL seq advance. |

---

## 3. Algorithms (T-035..T-062, excluding storage/retrieval)

Ingest adapters, chunking, extraction, consolidation, planner, answer composition, citation verification, psychometric scoring.

| ID | Conf | Statement |
|---|---|---|
| T-035 | MEDIUM | Ingest adapters (WhatsApp / Telegram / PDF / email) are thin parsers — no LLM — normalizing to canonical `Message[]`. Voice-note content requires transcription pre-adapter. |
| T-036 | MEDIUM | Chunking: window = 2000 tokens, overlap = 200 (10%), dialog-turn preserving. Tokenizer pending H-054 resolution. |
| T-037 | MEDIUM | Speaker preservation = inline `[Speaker:Timestamp]` markers retained verbatim + chunk-level header. |
| T-038 | MEDIUM | Each of 6 extraction prompts follows a common structural template (schema ref + 3–5 few-shots + relevance instruction + speaker-aware scoping). |
| T-040 | LOW | Sibling of T-039: separate post-extraction relevance-scoring LLM pass. Favor T-039 by parsimony. |
| T-041 | MEDIUM | Extraction failure = retry-with-exp-backoff (3 attempts, 500 ms base, ×2) → DLQ for transport; schema-violation tracking with partial-accept (5/6 domains persist). |
| T-043 | MEDIUM | Canonical post-parse representation = normalized `Message` object with per-message ULID for T-009 provenance. |
| T-046 | HIGH | **Load-bearing.** Consolidation = 3-stage hybrid: SHA-256 dedup → rule-based merge → LLM conflict escalation (<5% of events). Resolves §3.3/§4 "deterministic" contradiction. |
| T-047 | MEDIUM | Narrative summarization = per-category LLM call post-dedup on "major update" heuristic (≥5 new facts). O(1) per batch, ≤500 tokens per category. |
| T-048 | HIGH | **Externally confirmed.** Planner = GPT-4.1-mini with few-shot routing prompt. synthius.ai explicitly labels "Planner LLM". Compiles to ≤1,020 tokens within 1,100 budget; 12/12 routing probe correct. |
| T-049 | MEDIUM | Planner output = `{domains:[name], per_domain_query:{field, value, op}}` as OpenAI function-call payload. Render ≤100 tokens of 1,100 budget. |
| T-050 | MEDIUM | Misroute recovery = multi-domain fallback + second-attempt-then-refusal. Distinguishes true-refusal from misroute. Mean-preserving (~50 ms fallback on empty primary). |
| T-051 | MEDIUM | 1,100-token planner decomposes as ~350 system + 5×~120 few-shots + ~100 question + ~50 catalog. |
| T-052 | LOW | Sibling A: 1K answer system prompt = balanced 5-section composition (persona 300 + refusal 150 + format 150 + citation 100 + role 300). |
| T-053 | LOW | Sibling B: refusal-dominant composition (~600 refusal + format; ~100 persona). Both PASS; ablation-dependent. Carry as product options. |
| T-054 | MEDIUM | Retrieved context formatted as per-domain sections with field-level JSON blocks. Mitigates "lost in the middle" via structural cues. |
| T-055 | HIGH | **Load-bearing for 99.55%.** Refusal gate = dual-layer: programmatic hard-gate (zero-hits → canned refusal without answer LLM) + prompt-level soft-gate. Resolves G-044. |
| T-056 | MEDIUM | Citation verification = post-generation deterministic step; regex-extract fact-IDs and compare against retrieved-context ID set. O(answer_length). |
| T-057 | MEDIUM | Psychometrics injection = ~300-token "User personality:" block; Style ~100 tokens in adjacent "Writing style:" section; total persona footprint ~400 tokens. |
| T-058 | MEDIUM | Multi-domain aggregator concatenates per-domain FactItem blocks in planner-declared order with atomic no-mid-item truncation, NO cross-domain re-ranking. |
| T-059 | MEDIUM | Psychometric scoring = single-shot LLM per framework (9 calls / persona / cycle) producing full trait+facet output with evidence quotes. No per-NEO-PI-R-item scoring. |
| T-060 | MEDIUM | Psychometric update dynamics: re-derive from scratch at each consolidation batch; versioned in T-044 log. Winner over T-061 by Occam + evidence-quote compatibility. |
| T-061 | LOW | Sibling: EWMA-blend update (α ≈ 0.1–0.3). Under the evidence-quote requirement, forces a stateful top-N heap extension. Carry as LOW fallback. |
| T-062 | MEDIUM | Evidence + confidence: top-3 quotes per trait + `confidence = min(1.0, evidence_count / 5)`. 3-quote cap bounds psychometric prompt footprint. |

---

## 4. Ops & Cost (T-063..T-079, T-086..T-089)

Cost-model forensics (2× error localization, cross-table confusion typos), latency realism, capacity planning, vendor lock-in, batch-only posture.

| ID | Conf | Statement |
|---|---|---|
| T-063 | MEDIUM | §4/§3.3 "deterministic vs narrative" contradiction resolves via T-046 3-stage + T-047 separately-addressable summarization. Stages 1–2 cover ≥95% events deterministically. |
| T-064 | HIGH | §4.2 prose "99.9%" adversarial = stale-prose typo; Table 3's 99.55% canonical. 6 internal corroborations vs 1 outlier. |
| T-065 | HIGH | §4.2 prose "94.2%" temporal = cross-table confusion (Table 6 knowledge-type 94.40% copied into Table 3 LoCoMo-original 89.32% context). Inflationary 4.88 pp in context. |
| T-066 | HIGH | §4.2 prose "85.7%" multi-hop = stale-draft typo; Table 3's 94.34% canonical. Deflationary direction rules out fraud. |
| T-067 | HIGH | §4.3 prose gaps (+51.1/+57.7/+67.4/+39.1) = stale-prose typos; Table 5 canonical +56.33/+66.34/+62.52/+20.93. Mixed-direction deltas rule out inflation. |
| T-068 | HIGH | **Cost-model adjudication.** App. A.2's 4.7M/9.3M = isolated ~2× drafting inflation; Table 7's 5,040 tok/msg canonical. Three converging tests (USD back-solve, "Measured" label, savings-ratio 2.48×/5.03×). |
| T-069 | MEDIUM | §4.6 "<0.1% of total latency" = rhetorical overreach by one order of magnitude; realistic retrieval share 0.7–2.2% (21.79 ms / 1–3 s). |
| T-070 | MEDIUM | Production retrieval latency distribution at 200K facts: p50 ~5–10 ms, p95 ~25–40 ms, p99 ~50–100 ms. End-to-end p99 ≤ 3–5 s answer-bound. |
| T-071 | MEDIUM | Capacity: LLM-call-bound at ~100–1000 RPS/instance; per-persona storage negligible; $/persona/yr span $0.11–$181 by model. |
| T-072 | HIGH | Synthius-Mem is embarrassingly parallel per-persona; shard by `persona_id`; linear horizontal scaling; backpressure via per-tenant token-bucket + per-persona fairness. |
| T-073 | HIGH | Realistic production cost = 6,300–8,500 tok/msg (not Table 7's idealized 5,040) after consolidation + retries + migration + planner output. Corrected "~3.5–4.0×" framing. |
| T-074 | MEDIUM | Vendor lock-in mitigated via LiteLLM / OpenRouter / Portkey model-gateway layer; <5% latency overhead; abstracts OpenAI structured-output dependency. |
| T-075 | HIGH | Current pipeline is batch-only; streaming is §6 future work. Freshness SLO bounded by batch cadence. |
| T-077 | MEDIUM | Production quota handling = provider back-off (Retry-After) + per-tenant token-bucket + per-persona fairness. Retrieval path is Postgres-backed, decoupled from LLM quota. |
| T-078 | MEDIUM | Token cost curve is linear post-amortization: slope 5,040 tok/msg, intercept ~0. Crossover vs Full-Context at ~15 messages. |
| T-079 | MEDIUM | Decoding-parameter defaults (paper silent): T=0 for judge/extraction/planner; T=0.3–0.7 for answer. Any re-run MUST publish these. |
| T-086 | HIGH | 94.37% is pass@1 (single-shot). Zero paper hits on pass@k / best-of-k / self-consistency. |
| T-087 | MEDIUM | Reproducibility bundle needed: Dockerfile + LoCoMo snapshot + 6 extraction prompts + planner + judge + decoding params + storage DDL + CI gate. |
| T-088 | HIGH | **9-BLOCKER infra-only infeasibility.** Paper-only reproduction is infeasible; façade-reproduction feasible; exact numerical match requires author Q&A or source. |
| T-089 | MEDIUM | arXiv:2601.15313 miscitation: ID resolves but cited content is not in paper; reference absent from References. Two distinct errors. +40 pp scaling claim materially weakened. |

---

## 5. Evaluation & Reproducibility (T-080..T-096 subset)

Psychometric validity overreach, judge prompt inference, re-tagging IAA gap, same-family bias, metric-category errors, human-validation gap.

| ID | Conf | Statement |
|---|---|---|
| T-080 | MEDIUM | "9 validated frameworks" = instrument publication history, NOT Synthius-Mem scoring accuracy. §5.3 concedes method is unvalidated. |
| T-081 | MEDIUM | Judge prompt (unpublished) inferred as standard Zheng-2023 MT-Bench binary rubric. §4.1/§4.4/§5.3 triangulation. |
| T-082 | MEDIUM | 5-category knowledge-type re-tagging done without independent annotators or IAA (κ). Zero paper hits on inter-annotator / Cohen / kappa. |
| T-083 | HIGH | **MOST ARCHITECTURALLY CONSEQUENTIAL.** Judge-family asymmetry (Synthius self-judge vs baselines cross-judge) applies 6–16 pp combined confound to the 8.91 pp gap; architecture-only contribution = 0–3 pp (range includes zero). Erratum-worthy. |
| T-084 | MEDIUM | Zero human validation of judge decisions. Peripheral 57.66% particularly vulnerable. Recommend 100-question stratified spot-check + κ. |
| T-085 | HIGH | Per-persona isolation in LoCoMo: each participant gets full pipeline run with own turns as first-person; other participant's turns as third-party mentions (T-010 + G-058). |
| T-086 | HIGH | (Restated under Ops.) Pass@1. |
| T-087 | MEDIUM | (Restated under Ops.) Reproducibility bundle. |
| T-088 | HIGH | (Restated under Ops.) 9-BLOCKER infeasibility. |
| T-089 | MEDIUM | (Restated under Ops.) arXiv:2601.15313 miscitation. |
| T-090 | HIGH | "Exceeding human 87.9 F1" = metrics-category error (binary LLM-judge vs token-overlap F1). §5.3 itself acknowledges incomparability. Recommend erratum or F1 recomputation. |
| T-091 | MEDIUM | Marketing-voice overreaches in §4/§5: "market converged on LLM-as-judge", "virtually no competing system reports adversarial", "MemMachine unassessed". Erratum-class precision issues. |
| T-092 | MEDIUM | 3/3 spot-checked 2026 arXiv IDs (TiMem, SYNAPSE, MemMachine) resolve; IDs real. Cluster-unverified concern refuted. H-118 the exception (T-089). |
| T-093 | MEDIUM | Domain-generalization: 6 brain-inspired domains over-index on LoCoMo; zero cross-domain (medical/legal/tutoring/technical) held-out eval. |
| T-094 | MEDIUM | Per-component golden sets needed: extraction 100×6 / planner 100 / consolidator 50 conflict-pair / judge 100 human-assigned. |
| T-095 | MEDIUM | Lost-in-middle ablation missing; §5.1 names 4 mechanisms for +8.91 pp gap with no pp-per-mechanism attribution. Compounds T-083 fragility. |
| T-096 | HIGH | §1.1 "20 W brain" framing = non-load-bearing rhetorical dressing. Treat as motivational flair. |

---

## 6. Security & Privacy (T-097..T-113)

12-row STRIDE × stage failure catalog, 3-boundary threat model, prompt-injection defenses, data-poisoning defense, PII scrubbing, cross-persona attribute-as-claim, GDPR compliance, erasure, encryption/KMS, audit.

| ID | Conf | Statement |
|---|---|---|
| T-097 | MEDIUM | **Failure-mode catalog** = 12-row STRIDE × 8-stage register with {failure_mode, SLI, recovery_action, SLO_impact}. All 6 G-053 named failures covered. |
| T-098 | HIGH | **STRIDE 3-boundary threat model.** TB-1 untrusted-prose→LLM, TB-2 cross-persona, TB-3 multi-tenant. 18-cell matrix fully populated with ≥6 non-reducible cells. |
| T-099 | MEDIUM | Prompt-injection defense A: single-LLM guardrail sandwich + JSON-mode + closed-schema + regex denylist. 5/5 OWASP LLM01 canonical patterns blocked. Closed-schema load-bearing. |
| T-100 | HIGH | Prompt-injection defense B: separate detection-LLM pre-stage (Prompt-Guard-86M / Llama-Guard 3 / gpt-4.1-nano). Industry-standard per OWASP + MS Prompt Shield + NVIDIA NeMo. +0.46% on Table 7. Composes with T-099. |
| T-101 | MEDIUM | Data-poisoning defense: two-layer anomaly + drift audit. Layer 1 consolidation-time z-score / Jaccard / Levenshtein 0.83-threshold; Layer 2 weekly top-100 drift audit. 10/10 fixtures at ≤7-day latency. |
| T-102 | HIGH | **KEY forensic finding.** 99.55% "adversarial robustness" = FALSE-PREMISE QA refusal only. Zero paper hits on injection/jailbreak/poisoning/OWASP/NIST. 4 of 5 axes untested. Erratum-worthy. |
| T-103 | HIGH | Observability = OpenTelemetry + 12 SLIs + Grafana/Prometheus/Tempo. 4 SRE golden signals + 3 LLM-specific (quality / groundedness / judge-agreement). Fan-out-6 span native. |
| T-104 | HIGH | Failure/recovery = per-stage retry/DLQ + T-033 WAL replay + persona-bounded blast radius. RPO ≤100 ms / ≤10 ms; RTO ≤5 min. Composes T-018/T-032/T-033/T-041/T-042/T-046. |
| T-105 | HIGH | **Microsoft Presidio (Apache-2)** as hot pre-extraction PII stage. ≥40 PII entity types; F1 0.85–0.99; 5–30 ms/msg; tokenization + per-tenant vault. |
| T-106 | MEDIUM | Psychometric profiling ethics: no-act-on allowlist + inspect/suppress endpoint. 7 DENY-ALL fields (Political Compass / Moral Foundations / Kohlberg / IQ / health / address / biometric). GDPR Art. 6/9/15/16/17/22 + EU AI Act Annex III. |
| T-107 | HIGH | Cross-persona = attribute-as-claim-to-owner + explicit consent. Alice's mention of Bob is stored ONLY in A's Social-Circle as hearsay; migration into B requires consent-token. GDPR Art. 6(1)(a) + Art. 14. |
| T-108 | MEDIUM | GDPR/CCPA package: DPIA + regional residency matrix (EU/UK/US/CA/APAC) + DSAR endpoints + granular per-domain consent UI. GDPR Art. 12–23 + CCPA §1798.100–135. |
| T-109 | HIGH | **Right-to-erasure default:** two-tier soft-delete + crypto-shredding (NIST SP 800-88 Rev.1 §4.7). 30-day soft window + hard-delete via KMS DestroyKey on per-persona AES-256-GCM DEK. |
| T-110 | HIGH | Encryption: envelope encryption (per-persona DEK wrapped by per-tenant CMK in HSM) + TLS 1.3 (RFC 8446) + regional pinning. PCI-DSS v4.0 / HIPAA 164.312 / GDPR Art. 32 / FIPS 140-2. |
| T-111 | HIGH | Per-fact provenance extension: additive optional fields `injection_risk: number 0..1` (from T-100) + `pii_tokens_redacted` (from T-105). No breaking change to T-009. |
| T-112 | MEDIUM | Erasure sibling: tombstone-and-purge for single-region short-retention B2C. 30-day bounded residual. **FAILS** under long-retention backups / KMS-mandated sectoral regulation / multi-region. |
| T-113 | MEDIUM | Failure/recovery sibling: saga + circuit-breaker (Temporal.io / AWS Step Functions). Superior when LLM provider p99/p50 > 5× and outages >5 min ≥weekly. |

---

## 7. Integration & Multi-tenancy (T-114..T-126)

Tenant-scoped composite PK, integration contract, 8-op REST+gRPC surface, OAuth2 + ACL + RBAC, error envelope, deployment topology, platform scope.

| ID | Conf | Statement |
|---|---|---|
| T-114 | HIGH | **Tenant-scoped composite PK** `(tenant_id UUID, persona_id ULID)` + Postgres RLS + tenant_id propagation end-to-end. Shard-key `hash(tenant_id, persona_id) mod N`. Satisfies all 6 reviewer multi-tenant flags. |
| T-115 | MEDIUM | Deployment sibling A: hosted microservice at Synthius.ai with REST/gRPC SDK. |
| T-116 | MEDIUM | Deployment sibling B: MCP server exposing the 6-tool retrieval catalog + admin ops. Realizes §6 future-work item now. |
| T-117 | HIGH | **Integration contract: host owns Answer LLM.** Synthius-Mem returns structured facts + Psychometrics + Style. Reconciles Fig. 1 / §6 / §3.3 by reframing Fig. 1 as reference integration topology. |
| T-118 | MEDIUM | API sibling A: REST + gRPC + OpenAPI 3.1 dual-published, 8 operations (upload_conversation / get_persona / query / update / delete / add_psychometric_eval / list_personas / health). |
| T-119 | MEDIUM | API sibling B: gRPC-only Protobuf. Lower maintenance; higher web-integration friction. |
| T-120 | HIGH | OAuth2 + per-persona ACL (owner/editor/viewer) + org-level RBAC (admin/member/guest). OAuth2 token carries `tenant_id` feeding T-114 RLS. |
| T-121 | HIGH | Unified error envelope `{code, message, retry_hint, partial_result?, trace_id}` with 8-code taxonomy (EXTRACTION_MALFORMED / PLANNER_ROUTE_EMPTY / CONSOLIDATION_CONFLICT_UNRESOLVED / STORAGE_UNAVAILABLE / QUOTA_EXCEEDED / UNAUTHORIZED / TENANT_ISOLATION_VIOLATION / SCHEMA_VERSION_MISMATCH). |
| T-122 | MEDIUM | Relevance threshold = per-persona default (0.5) + per-request override. Resolves §5.2 peripheral trade at config surface. |
| T-123 | MEDIUM | Deployment topology: core microservice (3+ replicas) behind service mesh (Istio/Linkerd) + MCP sidecar for T-116 variant. Postgres primary + read replicas + Redis per-persona cache. |
| T-124 | HIGH | **Treat Synthius-Mem as research prototype + 500 MB pilot.** "Production" label has zero supporting operational metric. Architect MUST budget from-scratch hardening. |
| T-125 | MEDIUM | 5-item §6 roadmap: streaming ingest / MCP service (now via T-116) / federated extraction / memory decay / multi-agent shared memory with ACL. |
| T-126 | HIGH | **Broader Synthius platform undescribed.** Architect assumes externally provided layers: consent flow, inspect UI, disclosure policy, subject-access portals. Do NOT assume platform features not in scope. |

---

## Cross-references

Full evidence chains, SUPPORT/REFUTE verdicts, and peer-reviewer IDs live in `ledger/THEORIES.md`. Refuted sibling hypotheses with lesson-learned commentary live in `ledger/REFUTED.md`. The 11 revision-needed open questions live in `ledger/HYPOTHESES.md` revision-notes and are summarized in `04-OPEN-QUESTIONS.md`. Theory → evidence file mapping lives in `05-EVIDENCE-INDEX.md`.
