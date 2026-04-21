# Synthius-Mem Scientific Investigation — Design Spec

> Multi-agent scientific-method investigation of every gap identified in `docs/reports/synthius-mem-architecture-readiness/`. Promotes falsifiable hypotheses to theories via peer-reviewed experiments; produces architectural directives an architect can commit.

## 1. Purpose & Scope

**Purpose.** For every gap the 6 specialist reviewers identified in the Synthius-Mem architecture-readiness report, generate falsifiable hypotheses, subject them to peer-reviewed experiments, and promote survivors to theories. Produce a user-facing synthesis that turns theories into architectural directives and names the truly-open questions that must be escalated to the authors.

**Scope.**
- **Input paper:** arXiv:2604.11563v1 — Synthius-Mem (Gadzhiev & Kislov, Synthius.ai, April 2026).
- **Input reports:** `docs/reports/synthius-mem-architecture-readiness/{01,03,04,05,06,07,08,09}-*.md`.
- **Gap universe:** every gap at every severity — estimated ~200 entries across the 6 reviewer registers after dedup.
- **Scientific-method regime:** analytical + artifact construction + executable experiments (paper forensics / web research / prototype construction / LLM prompt probes). End-to-end LoCoMo reproduction is out of scope — the ground-truth prompts are unavailable.
- **Out of scope:** changes to the original 9 review files; contacting the paper authors; benchmarking against a real LLM API (we rely on sub-agent LLM probes for experiments).

## 2. Agent Cast

| Agent | Role | Context |
|---|---|---|
| **Coordinator** (orchestrator thread) | Owns the ledger, dispatches waves, appends to TRACE.jsonl, enforces author ≠ reviewer, decides wave boundaries and termination. Never authors hypotheses or reviews them. | Persistent |
| **Gap Cataloger** (Wave 0, once) | Reads the 6 reviewer reports; extracts every gap; deduplicates; assigns stable GAP-IDs; writes canonical `ledger/GAPS.md`. | Fresh |
| **Hypothesis Generator** | Per gap → 1-3 falsifiable hypotheses, each with (claim, prediction, disconfirmer). | Fresh per gap |
| **Experiment Designer** | Per hypothesis → experiment spec (method, pass/fail criterion, expected runtime). Immutable after design. | Fresh per hypothesis |
| **Experiment Runner** | Executes experiment → writes raw evidence file under `evidence/`. Four method families: paper-forensic, external-evidence, artifact-construction, LLM-prompt-probe. | Fresh per experiment |
| **Peer Reviewer** | Different agent instance than the hypothesis's Generator. Rules SUPPORT / REFUTE / INCONCLUSIVE with cited evidence. | Fresh per evidence bundle |
| **Adjudicator** | Final verdict: PROMOTE / REFUTE / REVISION_NEEDED. Loop limit 3 revisions → REVISION_EXHAUSTED. | Fresh per hypothesis |
| **Synthesizer** (once, end) | Produces the 6 user-facing reports from the complete ledger. | Fresh |

**Peer-review contract:** the Coordinator tracks which agent instance produced each hypothesis and refuses to dispatch that same "Generator session" as its own Reviewer. (Sub-agents have fresh context anyway, but we also record `author_agent_tag` and `reviewer_agent_tag` to enforce at the ledger level.)

## 3. Ledger (state model)

All under `docs/reports/synthius-mem-scientific-investigation/ledger/`.

| File | Schema | Purpose |
|---|---|---|
| `GAPS.md` | Markdown table: GAP-ID, severity, source-file, title, description, verbatim-quote, canonical-group | Master gap list |
| `HYPOTHESES.md` | Table: HYPO-ID, GAP-ID, claim, prediction, disconfirmer, state, author_tag | Every hypothesis |
| `EXPERIMENTS.md` | Table: EXP-ID, HYPO-ID, method, pass/fail-criterion, expected-runtime, evidence-file-path, outcome | Every experiment |
| `REVIEWS.md` | Table: REV-ID, EXP-ID, reviewer_tag, verdict, rationale, evidence-cited | Every peer review |
| `THEORIES.md` | Table: THEORY-ID, derived-from-HYPO-ID, statement, evidence-index, confidence | Promoted theories |
| `REFUTED.md` | Table: HYPO-ID, reason, refuting-evidence, lesson-learned | Graveyard |
| `WAVES.md` | Per-wave dashboard: wave, gap-count, promoted, refuted, revision-exhausted, in-progress | Live status |
| `TRACE.jsonl` | JSON-lines: `{ts, actor, action, from_state, to_state, gap_id, hypo_id, exp_id, artifact}` | Append-only event log; TODO/WIP/DONE source of truth; supports resume-after-crash |

**State machine per (gap, hypothesis):**

```
OPEN → HYPOTHESIZED → DESIGNED → RUNNING → EVIDENCE → REVIEWED →
  { PROMOTED, REFUTED, REVISION → HYPOTHESIZED (≤3×) → REVISION_EXHAUSTED }
```

Every state transition produces a TRACE.jsonl line.

## 4. Wave Plan

Waves are themed to respect dependency — earlier waves' theories constrain later waves' experiment design.

| Wave | Theme | Rough gap scope | Depends on |
|:---:|---|---|---|
| 0 | Catalog | ~200 dedup | — |
| 1 | Schemas (6 domain JSON) | D1-D10 + related keystone gaps | — |
| 2 | Storage, CategoryRAG, matching primitive | D3-D8, ALG-E | Wave 1 |
| 3 | Algorithms (extract/plan/consolidate/answer/diff/psychometric) | ALG-A to ALG-I (~49 gaps) | Waves 1-2 |
| 4 | Ops, cost model, scaling, latency | OPS-01 to OPS-23, C-13 (2× error) | Wave 3 |
| 5 | Security, privacy, threat model, GDPR, ethics | Q-1 to Q-30 | — |
| 6 | Integration contract + multi-tenancy | C-01 to C-03, OPS-06, Q-16 | Waves 1-4 |
| 7 | Long-tail cleanup (MINOR/NIT) | remainder | — |

Within a wave: all gap investigations fan out in parallel. Between waves: sequential.

## 5. Scientific-Method Lifecycle

**Per hypothesis:**

1. Generator writes `(claim, prediction, disconfirmer)` to `HYPOTHESES.md`, state = HYPOTHESIZED.
2. Designer writes `(method, pass/fail_criterion, expected_runtime)` to `EXPERIMENTS.md`, state = DESIGNED. **Spec immutable afterward.**
3. Runner writes evidence file under `evidence/<EXP-ID>.md`, state = RUNNING → EVIDENCE.
4. Peer Reviewer (enforced distinct from Generator) writes `REVIEWS.md` entry, state = REVIEWED.
5. Adjudicator rules and sets state PROMOTED / REFUTED / REVISION_NEEDED.
6. REVISION_NEEDED → loop back to step 1 with refuting evidence as input constraint. Cap 3 loops → REVISION_EXHAUSTED (surfaces in `04-OPEN-QUESTIONS.md`).

**Promotion criteria (all must hold):**
- ≥1 experiment returned SUPPORT verdict from peer review.
- No unrefuted REFUTE verdict on a parallel experiment of the same hypothesis.
- Adjudicator confirms disconfirmer was testable and the experiment actually tested it.

## 6. Experiment Method Families

1. **Paper-forensic** — agent re-reads paper with the hypothesis as a narrow lens; outputs every paper-text observation that supports or refutes; cites page numbers.
2. **External-evidence** — WebFetch/WebSearch on Synthius.ai, GitHub repos of cited systems (Mem0, MemMachine, MemOS, LangMem), arXiv abstracts of cited papers; outputs cited-evidence bundle.
3. **Artifact-construction** — agent drafts a candidate artifact (JSON schema, extraction prompt, planner prompt, pseudo-code) from paper constraints; runs internal-consistency checks (does it satisfy stated behaviors, sizes, and timing claims?).
4. **LLM-prompt-probe** — agent spawns a short-lived sub-agent acting as extractor / planner / consolidator, runs it on a synthetic tiny fixture (a hand-crafted Alice-and-Bob conversation), measures schema-conformance / domain-routing / dedup behavior; compares to paper's stated behavior.

## 7. Output Artifacts (Synthesizer's deliverables)

Under `docs/reports/synthius-mem-scientific-investigation/` (sibling to `ledger/` and `evidence/`):

| File | Purpose |
|---|---|
| `00-EXECUTIVE-SUMMARY.md` | Verdict + top 10 promoted theories + headline directives |
| `01-THEORIES.md` | Every promoted theory with evidence chain |
| `02-ARCHITECTURAL-DIRECTIVES.md` | Theories translated into commit-able architectural rules (e.g., "Use JSONB + GIN indexes for per-persona store", "Extraction LLM MUST use JSON-mode structured outputs with schema validation") |
| `03-REFUTED-HYPOTHESES.md` | Graveyard with lessons learned |
| `04-OPEN-QUESTIONS.md` | Gaps where all hypotheses were refuted or REVISION_EXHAUSTED — the must-ask-authors list |
| `05-EVIDENCE-INDEX.md` | Theory → supporting evidence file paths |

The `ledger/` files themselves are preserved for audit.

## 8. Termination Criteria

**Per-wave:** all gaps in the wave have reached PROMOTED / REFUTED / REVISION_EXHAUSTED.

**System-level:**
- All 7 waves terminate → normal completion.
- OR Coordinator declares diminishing returns on long-tail Wave 7 if promotion rate < 10% over the last 10 processed gaps AND those gaps' max severity ≤ MINOR.

## 9. Guardrails

- **Author ≠ Reviewer** enforced at dispatch via `author_tag` / `reviewer_tag` comparison.
- **3-revision cap** per hypothesis prevents infinite loops.
- **Experiment spec immutable** after design — Runner can't reinterpret pass/fail.
- **TRACE.jsonl append-only** — no rewrites; supports full resume-after-crash.
- **2 consecutive malformed specialist outputs** → hypothesis marked NEEDS_HUMAN, surfaces in OPEN-QUESTIONS.
- **Fresh context per specialist** — agents read only the minimum files; paths passed, not content dumps.
- **Cost envelope** — Coordinator tracks cumulative sub-agent token usage in TRACE.jsonl; pauses and asks user to confirm continuation if it exceeds 2M tokens before Wave 4 completes, or 5M tokens total.
- **Non-overlapping parallel work** — within a wave, each specialist gets a distinct gap/hypo/exp assignment; Coordinator never double-dispatches.

## 10. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Runaway loops (hypothesis chain infinite) | Medium | 3-revision cap; REVISION_EXHAUSTED terminal state |
| Author-pretending-to-be-reviewer | Low (fresh context by design) | `author_tag` / `reviewer_tag` record + dispatch-time check |
| Fabricated evidence from specialist agents | Medium | Evidence files must cite paper pages, web URLs, or artifact paths; Reviewer validates citation integrity |
| Drift from paper's actual claims | Medium | Every evidence file must include a verbatim paper quote for the referenced claim |
| Context exhaustion in Coordinator (main thread) | Medium | Ledger lives on disk; Coordinator reads only WAVES.md + current wave's dispatch tasks; everything else flows through sub-agents |
| Theories promoted on too-thin evidence | Medium | Promotion requires ≥1 SUPPORT from peer-reviewed experiment; Adjudicator prompts enforce disconfirmer was truly testable |

## 11. Success Criteria

- Every gap in the catalog reaches a terminal state (PROMOTED / REFUTED / REVISION_EXHAUSTED / NEEDS_HUMAN).
- At least one promoted theory per dimension (components, data, algos, ops, security/privacy, integration) — or the OPEN-QUESTIONS doc explains why that dimension yielded no theories.
- Cost-model 2× inconsistency (C-13) is conclusively resolved (promoted or refuted) — this is the most visible correctness failure in the paper.
- `02-ARCHITECTURAL-DIRECTIVES.md` is actionable enough that an architect can start design from it.
- Entire investigation is auditable: every theory traces to evidence files, every state transition traces to a TRACE.jsonl line.

---

*Design approved 2026-04-21. Spec committed to git before execution begins. Treated as executable plan — no separate writing-plans skill invocation required under YOLO mode.*
