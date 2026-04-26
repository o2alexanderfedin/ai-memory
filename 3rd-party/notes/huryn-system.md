# huryn-system — research note

**Subject 02** in the Claude Code Memory Systems Survey. Notes-only;
no clone (the system has no public GitHub repo).

**Authors.** Paweł Huryn (Product Compass) seeded the pattern; John
Conneely (Young Leaders in Tech, issue #98, 18 Mar 2026) extended it.
One lineage, two depths.

**What it is.** A CLAUDE.md-driven discipline: tell Claude to append
dated learnings (`date — what — why`) to `.claude/memory.md` and to
read that file at session start. Conneely splits memory into a folder
hierarchy (`~/.claude/memory/{general.md,tools/*,domain/*}`) with
**routing rules in CLAUDE.md** and content in topic files (because
Anthropic caps project `MEMORY.md` at 200 lines). Conneely adds an
optional PreToolUse hook (`pre-tool-memory.sh` + `.py`, keyed on PPID,
~5 ms after first call) that injects the memory index once per session.
Huryn's later "Learning" block tells Claude to actively manage the
files — merge, split, prune, propose CLAUDE.md edits.

**Why it matters here.** Lowest-effort, zero-infra end of the spectrum
versus our typed multi-tenant `ai-memory` service. Useful as the
"baseline anyone can deploy in 5 minutes" comparison row.

**Findings:** `notes/cc-memory-systems-survey/findings/02-huryn-system.md`.
**Evidence:** youngleaders.tech/p/how-i-finally-sorted-my-claude-code-memory; substack.com/@huryn notes c-216337711, c-228204100, c-228883267.
