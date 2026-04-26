# 02 — Huryn / Conneely CLAUDE.md Memory System

Subject **02** in the Claude Code Memory Systems Survey. Common slug:
`huryn-system`. Two authors, one lineage: **Paweł Huryn** published the
seed pattern on Substack ("paste this into your `claude.md`"); **John
Conneely** ("Young Leaders in Tech" issue #98) extended it into a
folder-structured, hook-injected variant and credits Huryn explicitly.
This findings file covers the combined pattern and notes where the two
diverge.

## Dimension table

| # | Dimension | Value |
|---|---|---|
| A1 | name | Huryn / Conneely CLAUDE.md memory pattern |
| A2 | vendor_or_author | Paweł Huryn (The Product Compass) + John Conneely (Young Leaders in Tech) |
| A3 | license | unknown (pasteable snippets in newsletters; no LICENSE file published) |
| A4 | source_availability | docs-only |
| A5 | video_level | 2 |
| A6 | maturity | active (Huryn note Feb 2026; Conneely article 18 Mar 2026) |
| B1 | storage_backend | markdown-files |
| B2 | retrieval_mechanism | keyword (Claude reads files by name from CLAUDE.md routing rules) |
| B3 | write_path | agentic (Claude itself appends to `memory.md` when CLAUDE.md tells it to) |
| B4 | update_model | append-only (with periodic agent-driven merge/split per Huryn's "Learning" block) |
| B5 | memory_unit | file (and per-line dated entry inside it) |
| B6 | schema_shape | semi-structured (`date — what — why` lines, free-form prose otherwise) |
| C1 | write_latency | unknown (markdown append; effectively sub-ms but unbenchmarked) |
| C2 | read_latency | unknown; Conneely cites hook overhead "~80 ms first call, ~5 ms after" |
| C3 | recall_accuracy | unknown (no benchmark; anecdotal — Huryn reports "24 self-written rules by week 3") |
| C4 | scale_ceiling | Anthropic-imposed 200-line cap on project `MEMORY.md` at session start; CLAUDE.md loads in full |
| C5 | token_overhead_per_turn | unknown; bounded by ≤ 200 lines of MEMORY.md + CLAUDE.md routing block per session start (hook injects once per PPID, not per turn) |
| C6 | cost_model | $0 infra; cost = extra tokens per session start |
| D1 | cc_integration | CLAUDE.md (Huryn baseline) + hook (Conneely PreToolUse extension) + slash-command (`/memory` from Anthropic native, used opportunistically) |
| D2 | other_clients | none (CLAUDE.md format is Claude-Code-specific; same files could be hand-fed to other clients but no integration) |
| D3 | protocols | none |
| D4 | lock_in_level | low |
| D5 | composability | composes-with: Anthropic native auto-memory (`MEMORY.md`), `claude-mem` plugin |
| E1 | setup_complexity | 1 (Huryn baseline: paste a block) — 2 (Conneely full: also drop two hook scripts + edit `settings.json`) |
| E2 | maintenance_burden | low; Huryn's "Learning" block explicitly tells Claude to merge/split/prune files itself |
| E3 | observability | logs (the memory files themselves are human-readable; hook stderr if scripted) |
| E4 | failure_modes | Routing rules misplaced into project `MEMORY.md` get truncated by 200-line cap; flat monolithic CLAUDE.md inflates every session; tool-MCP token blowups (Conneely banned Atlassian MCP). |
| E5 | data_locality | local-only |
| E6 | privacy_posture | All memory stays in repo / `~/.claude`; no network egress beyond Claude API itself. No encryption/multi-tenant story documented. |
| F1 | best_fit | Solo developer who wants persistent project memory in plain markdown without running services or DBs. |
| F2 | anti_patterns | Teams that need shared, queryable memory across many engineers; workflows requiring semantic recall over thousands of entries. |
| F3 | not_for | High-volume conversation logging; embedding-based retrieval; cross-tenant isolation. |
| F4 | evidence_links | (see below) |
| G1 | relation_to_host_repo | Same goal as `ai-memory` (give Claude persistent project context) but at the opposite end of the spectrum: Huryn/Conneely is markdown-only, agent-managed, zero-infra. `ai-memory` is a typed multi-tenant service. They compose: `ai-memory` could back the same CLAUDE.md routing pattern. |
| G2 | open_questions | (see below) |

### F4 — evidence links

- Conneely, "How I Finally Sorted My Claude Code Memory" (#98), Young Leaders in Tech, 18 Mar 2026 — https://www.youngleaders.tech/p/how-i-finally-sorted-my-claude-code-memory
- Huryn, Substack note c-216337711 ("How to Give Claude Code Memory") — https://substack.com/@huryn/note/c-216337711
- Huryn, Substack note c-228204100 ("Learning" block for CLAUDE.md) — https://substack.com/@huryn/note/c-228204100
- Huryn, Substack note c-228883267 (Knowledge Architecture / Decision Journal / Quality Gate) — https://substack.com/@huryn/note/c-228883267
- Huryn, "The Guide to Claude Code for PMs", The Product Compass — https://www.productcompass.pm/p/claude-code-guide

## Long form (≤ 800 words)

### Who, what, lineage

Paweł Huryn (Product Compass) published the seed: a short "Memory
Management" block you paste into your project's `claude.md`, instructing
Claude to append discoveries (`date — what — why`) to
`.claude/memory.md` and to read that file at every session start. Cost:
near-zero tokens; survives compaction and crashes. He later layered on a
**Learning** block (Domain vs Procedural knowledge, hierarchical
`knowledge/index.md`, error-log graduation) and a three-block
"Knowledge Architecture / Decision Journal / Quality Gate" framework.

John Conneely, writing as Young Leaders in Tech (issue #98, "How I
Finally Sorted My Claude Code Memory"), credits Huryn and extends the
pattern from one flat file into a folder hierarchy plus an automatic
PreToolUse hook. So the survey subject is best understood as **one
shared lineage with two depths**: Huryn-baseline (paste a block) and
Conneely-full (folders + hook).

### Mechanism

**Storage.** Plain markdown under `~/.claude/memory/` (global) and
`<repo>/.claude/memory/` (project). Conneely's layout:

```
~/.claude/
├── CLAUDE.md            # 63 lines, down from 189
├── memory/
│   ├── memory.md        # index
│   ├── general.md
│   ├── tools/{snowflake,atlassian,slack}.md
│   └── domain/{topic}/
└── hooks/
    ├── pre-tool-memory.sh
    └── pre-tool-memory.py
```

Per-project memory at `~/.claude/projects/<mapped-path>/memory/MEMORY.md`,
where `<mapped-path>` is the project path with `/` and `.` rewritten as `-`.

**Routing.** CLAUDE.md (which loads in full) holds *pointers* — "if you
need Snowflake, read `memory/tools/snowflake.md`". The actual content
sits in topic files that load only when needed. Conneely's stated
mistake: putting routing rules inside the project `MEMORY.md`, which
Anthropic truncates at 200 lines, so routing rules got lost. Lesson:
routing in `CLAUDE.md`, content in topic files.

**Write path.** Agentic. The CLAUDE.md instruction tells Claude to
append entries itself when it learns something (architectural decisions,
gotchas, env quirks). Huryn's "Learning" block explicitly directs
Claude to *manage* the knowledge base — merge overlapping categories,
split long files, propose CLAUDE.md edits proactively.

**Read path / hook (Conneely only).** A PreToolUse hook bash-wrapper
runs `pre-tool-memory.py`, which:

- keys off `os.getppid()` (no `CLAUDE_SESSION_ID` env var exists),
- maps cwd → `~/.claude/projects/<mapped-path>/`,
- reads up to 200 lines of `MEMORY.md`,
- emits the global memory index,
- returns JSON for Claude Code's hook protocol.

The shell wrapper checks a flag at `/tmp/claude-memory-loaded-<PPID>` so
the python only runs once per session (~80 ms first call, ~5 ms after).
Registered in `settings.json` under `PreToolUse` with matcher `"*"` and
`timeout: 5`.

### Domain knowledge lifecycle

Three-stage promotion path: **Staging** (`domain/<name>/` accumulates
notes) → **Promotion** (package as a Skill/Plugin) → **Pointer** (the
memory file becomes a one-liner pointing at the now-canonical Skill).
This is how informal memory graduates into reusable tooling.

### Failure modes the authors flag

- Routing rules in `MEMORY.md` get cut off by the 200-line cap.
- Monolithic CLAUDE.md (Conneely was at 189 lines) eats every session's
  context budget; topic-file split is the fix.
- Tool MCPs that hemorrhage tokens (Conneely banned Atlassian MCP and
  switched to ACLI/REST).
- Knowledge drift when work happens piecemeal across locations —
  centralization in `memory/` prevents diverging answers.
- "Memory without reflection is just storage" (Huryn): without the
  Learning block telling Claude to actively prune/merge, files turn
  into ever-growing correction logs.

### What does *not* exist

- **No public GitHub repo** for either author's memory system. The
  Conneely article ships two prompts (Part 1 = structure, Part 2 =
  hook) you paste into Claude Code in plan mode; the python/bash hook
  source is reproduced inside the article itself. Conneely has
  separately released "The Skills Toolkit" plugin, but that is not the
  memory system.
- No license, no benchmark, no telemetry, no cloud component.

### Relation to subject 09 (`ai-memory`)

Same goal — durable project context for Claude Code — at opposite ends
of the spectrum. Huryn/Conneely: markdown, agent-managed, zero infra,
local-only, low lock-in. `ai-memory`: typed multi-tenant service with
auth and APIs. They are not competitors; the CLAUDE.md routing pattern
could just as easily route Claude to call `ai-memory` instead of read
a `.md` file.

### Open questions (G2)

- Exact line counts / token cost of Huryn's full three-block
  (Knowledge Architecture + Decision Journal + Quality Gate) system —
  the canonical post is paywalled past the teaser.
- Whether Conneely has since published the hook scripts to GitHub
  (he mentioned weekend plans for an "Eval Committee" upload, unrelated
  to memory, in comments).
- Empirical recall accuracy: only anecdote ("24 self-written rules by
  week three") — no LoCoMo / MemBench numbers.
