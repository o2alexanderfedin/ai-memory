# PLAN — Claude Code Memory Systems Survey

**Coordinator:** this file. **Scope:** see [BRIEF.md](BRIEF.md). **Schema:** [DIMENSIONS.md](DIMENSIONS.md).

## 1. Subject roster & brief assignments

| NN | Subject | Slug | Brief |
|---|---|---|---|
| 01 | Native Claude Code memory | `native-claude-code` | [briefs/01-native-claude-code.md](briefs/01-native-claude-code.md) |
| 02 | John & Paweł's system | `huryn-system` | [briefs/02-huryn-system.md](briefs/02-huryn-system.md) |
| 03 | Memsearch | `memsearch` | [briefs/03-memsearch.md](briefs/03-memsearch.md) |
| 04 | MemPalace | `mempalace` | [briefs/04-mempalace.md](briefs/04-mempalace.md) |
| 05 | LLM Wiki (Karpathy) | `karpathy-llm-wiki` | [briefs/05-karpathy-llm-wiki.md](briefs/05-karpathy-llm-wiki.md) |
| 06 | Recall.it | `recall-it` | [briefs/06-recall-it.md](briefs/06-recall-it.md) |
| 07 | Mem0 | `mem0` | [briefs/07-mem0.md](briefs/07-mem0.md) |
| 08 | OpenBrain | `openbrain` | [briefs/08-openbrain.md](briefs/08-openbrain.md) |
| 09 | This repo (`ai-memory`) | `ai-memory-host` | [briefs/09-ai-memory-host.md](briefs/09-ai-memory-host.md) |

## 2. Sequencing

```
                   [Coordinator]                          (this stage — done after these 3 artifacts land)
                        │
        ┌───────────────┴────────────┐
        │                            │
   [Researcher pool — parallel, one agent per subject 01..09]
   Each: read its brief + DIMENSIONS.md → write findings/<NN>-<slug>.md
                                              + 3rd-party/notes/<slug>.md
                                              + INDEX.md row (parent registry)
        │
        ▼
   [Synthesizer]   reads all findings/*  → writes DRAFT-REPORT.md
        │
        ▼
   [Reviewer]      reads DRAFT          → writes REVIEW-1.md
        │
        ▼
   loop (cap 3):  Synthesizer revises → Reviewer scores again
        │
        ▼
   [Synthesizer]  promotes DRAFT → FINAL-REPORT.md  (only when reviewer says "converged")
```

- All 9 researchers run in parallel; none depend on each other.
- Synthesis is strictly serial after **all** 9 findings exist.
- Main thread updates `STATE.md` after each agent returns.

## 3. Synthesizer + Reviewer protocol

**Cap:** 3 review rounds. After round 3, promote whatever the synthesizer has and flag unresolved items in an "Open issues" section of `FINAL-REPORT.md`.

**Synthesizer tasks (per round):**
1. Build the comparison matrix from `findings/*` using DIMENSIONS.md as columns.
2. Fill the BRIEF.md deliverables: comparison table, performance numbers, applicability, integration points (incl. cross-subject composition), useful background.
3. Flag every `unknown` cell — don't paper over gaps.
4. Track changes since the previous round at the top under `## Changelog`.

**Reviewer checks (each round writes `REVIEW-<N>.md`):**
- **Coverage** — every subject filled every required dimension (or marked `unknown` with rationale)?
- **Apples-to-apples** — units consistent? Same definitions across rows?
- **Source-backed** — every numeric claim cites a URL or file?
- **Taxonomy fidelity** — does the report reproduce the video's 6-level scheme correctly, or explain divergence?
- **Cross-subject claims** — composition/competition assertions justified?
- **Self-positioning** — subject 09 (host repo) treated with the same rigor, not as a foregone winner?
- **Verdict** — one of: `converged`, `revise (issues listed)`, `block (major rework)`.

**Convergence criteria:**
- Reviewer verdict is `converged`, **or**
- 3 rounds completed and remaining issues are all flagged under "Open issues".

## 4. Researcher operating rules

- Read `briefs/<NN>-<slug>.md` first, then `DIMENSIONS.md`. Do not read other researchers' findings — keep the work independent.
- Cloning is encouraged for OSS subjects (briefs say yes/no/optional). Hosted SaaS → public docs only.
- If sources contradict, record both with citations and pick the most recent or most official as primary.
- Length budgets are caps, not targets. Concise > exhaustive.
- After finishing, append the row provided in the brief to `/Users/alexanderfedin/Projects/ai-memory/3rd-party/INDEX.md` and write `3rd-party/notes/<slug>.md`.

## 5. Risks & open questions for clarification

- **R1. Video taxonomy access.** None of us have transcribed Simon Scrapes' video. Researchers must rely on the level labels in BRIEF.md plus secondary blog/Substack posts. If a level boundary is ambiguous, report the ambiguity rather than inventing one.
- **R2. "John & Paweł's system" identity.** BRIEF.md links `youngleaders.tech` and `substack.com/@huryn`. Researcher 02 must confirm both authors and link the canonical write-up before treating it as a single coherent system.
- **R3. Karpathy "LLM Wiki" stability.** It's a gist, which can edit-in-place without history. Researcher 05 must pin a revision (gist permalink with hash) so claims are reproducible.
- **R4. Hosted-SaaS opacity.** Mem0 and Recall.it expose only marketing + SDK docs. Performance numbers will frequently be `unknown`; that is the correct outcome — do not extrapolate from competitor benchmarks.
- **R5. Self-positioning bias on subject 09.** The host repo is also the survey commissioner. Researcher 09 should describe it neutrally; the synthesizer must not let it grade itself favorably.
- **R6. Composability claims.** Whether two systems "compose" is often aspirational. Only mark `composes-with:X` when there's a documented integration path (MCP server, plugin, blog post). Otherwise → `standalone` + a note.
- **R7. Level 6 ("single brain for ALL tools") evaluation.** Both Mem0 and OpenBrain claim Level 6. Synthesizer must articulate the differentiator rather than collapsing them.

## 6. Definition of done (recap from BRIEF.md)

- `FINAL-REPORT.md` exists, reviewer-approved.
- `findings/01..09-*.md` all present and conforming to DIMENSIONS.md.
- Each subject registered in `/Users/alexanderfedin/Projects/ai-memory/3rd-party/INDEX.md`.
- `STATE.md` reflects all artifacts.
