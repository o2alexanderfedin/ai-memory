# Research Subjects Index

Registry of every external repository cloned into `3rd-party/`. See
[README.md](README.md) for the conventions.

| Subject | Upstream | Pinned commit | Related research | Status | Added | Notes |
|---|---|---|---|---|---|---|
| Native Claude Code memory | https://docs.claude.com/en/docs/claude-code/memory | n/a (vendor docs) | Claude Code Memory Systems Survey | notes-only | 2026-04-25 | Built-in CLAUDE.md system, Level 1 |
| memsearch | https://github.com/zilliztech/memsearch | a3e621f63d52b65de2427cb5aadb65a6d95af3ab | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 3 — semantic memory via Milvus |
| Karpathy LLM Wiki | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/ac46de1ad27f92b28ac95459c782c07f6b8c964a | ac46de1ad27f92b28ac95459c782c07f6b8c964a | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 2 — personal wiki pattern; idea file, no code |
| Recall.it | https://www.recall.it/ | n/a (SaaS) | Claude Code Memory Systems Survey | notes-only | 2026-04-25 | Level 4 — verbatim conversation recall (label disputed; see findings) |
| OpenBrain | https://github.com/NateBJones-Projects/OB1 | 7bbc37e274d1b3cbfbd35049f7174a46042765e9 | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 6 — single-brain alternative to Mem0 |
| Huryn CLAUDE.md system | https://substack.com/@huryn | n/a | Claude Code Memory Systems Survey | notes-only | 2026-04-25 | Level 2 — disciplined CLAUDE.md recall |
| MemPalace | https://github.com/MemPalace/mempalace | 5e574045028d1b6fb9ead3569cdf21c47bd3c4df | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 5 — self-organizing knowledge base |
| ai-memory (host) | (this repo — no clone) | n/a (working tree) | Claude Code Memory Systems Survey | self | 2026-04-25 | Survey subject 09 — typed persona-memory backend |
| Mem0 | https://github.com/mem0ai/mem0 | bd9d27ff509f6259c3bfd1915ca4c975db798c8a | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 6 — cross-tool memory backend (OSS + SaaS) |

## Status legend

- **active** — currently being investigated; clone expected on disk.
- **paused** — investigation on hold; clone may or may not be on disk.
- **archived** — investigation closed; notes retained, clone may be removed.

## Pending migrations

Clones that exist elsewhere and should be relocated into this directory:

- `docs/reports/synthius-mem-scientific-investigation/ledger/hupyy-cpp-to-rust/`
  — full Rust repo currently sitting inside the investigation ledger. When
  next touched, move to `3rd-party/hupyy-cpp-to-rust/` and add an INDEX row
  pointing back to the ledger that motivated it.

## Active research projects

Multi-subject investigations that span several entries in this index:

| Research | Working dir | Status | Started |
|---|---|---|---|
| Claude Code Memory Systems Survey | [`notes/cc-memory-systems-survey/`](notes/cc-memory-systems-survey/) | active | 2026-04-25 |
