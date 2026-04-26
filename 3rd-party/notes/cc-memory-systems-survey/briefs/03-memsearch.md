# Brief 03 — Memsearch

- **Name:** Memsearch (Zilliz)
- **Slug:** `memsearch`
- **Video level:** 3 ("Search by meaning, not just keywords")
- **Source URLs:**
  - https://github.com/zilliztech/memsearch
  - Zilliz / Milvus blog (search "memsearch" on https://zilliz.com/blog)

## Cloning guidance

**Yes.** Clone to `3rd-party/memsearch/`. Pin the commit you read.

```
cd /Users/alexanderfedin/Projects/ai-memory/3rd-party
git clone https://github.com/zilliztech/memsearch.git memsearch
```

## Investigation steps

1. README + architecture docs in the clone — capture storage backend (likely Milvus / Zilliz Cloud) and embedding model.
2. How does it ingest? Hooks into Claude Code? CLI? MCP? Scheduled scrape?
3. Write-path: what triggers a memory write? Auto-extracted from transcripts, or explicit `add` calls?
4. Read-path: top-k semantic search? Hybrid with metadata filter?
5. Any benchmarks in the repo (`bench/`, `evals/`) or referenced in the README.
6. Note license + maintenance signal (last commit date, open issues).

## Output

- **Findings:** `findings/03-memsearch.md` — DIMENSIONS table + ≤ 800 words.
- **Notes:** `3rd-party/notes/memsearch.md` — ≤ 200 words.
- **Format:** see DIMENSIONS.md.

## INDEX.md row to add

```
| memsearch | https://github.com/zilliztech/memsearch | <commit-hash> | Claude Code Memory Systems Survey | active | 2026-04-25 | Level 3 — semantic memory via Milvus |
```
