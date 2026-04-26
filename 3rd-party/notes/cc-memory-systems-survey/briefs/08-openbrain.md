# Brief 08 — OpenBrain

- **Name:** OpenBrain (Nate B. Jones)
- **Slug:** `openbrain`
- **Video level:** 6 ("A single brain for ALL your AI tools")
- **Source URLs:**
  - https://github.com/NateBJones-Project... (full slug to resolve — likely `NateBJones-Project/openbrain` or similar)
  - Nate B. Jones' channels (Substack/YouTube/X) for context

## Cloning guidance

**Yes.** Clone to `3rd-party/openbrain/`. Pin the commit.

```
cd /Users/alexanderfedin/Projects/ai-memory/3rd-party
git clone https://github.com/NateBJones-Project... openbrain
```

## Investigation steps

1. Resolve the truncated GitHub URL — confirm the canonical org/repo before cloning.
2. README + repo layout. Capture: storage backend, ingestion model, retrieval mechanism.
3. "Single brain" claim: how does it federate across tools? MCP? Custom adapters per tool?
4. Compare to Mem0 (subject 07) — write a side-by-side note inside your findings under `relation_to_host_repo` or in prose. Synthesizer needs the differentiator.
5. License + maintenance signal.
6. Capture any benchmark or self-reported metric.

## Output

- **Findings:** `findings/08-openbrain.md` — DIMENSIONS table + ≤ 800 words.
- **Notes:** `3rd-party/notes/openbrain.md` — ≤ 200 words.
- **Format:** see DIMENSIONS.md.

## INDEX.md row to add

```
| OpenBrain | <resolved-github-url> | <commit-hash> | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 6 — single-brain alternative to Mem0 |
```
