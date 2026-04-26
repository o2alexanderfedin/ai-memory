# Brief 06 — Recall.it

- **Name:** Recall.it
- **Slug:** `recall-it`
- **Video level:** 4 ("Recall verbatim conversations")
- **Source URLs:**
  - https://www.recall.it/
  - Any docs subdomain (e.g., `docs.recall.it`)
  - Their pricing/API page
  - Public changelog or blog if available

## Cloning guidance

**No.** Hosted SaaS, no public source. Research via marketing site, docs, SDK references, and any third-party reviews.

## Investigation steps

1. Crawl recall.it landing + docs. Capture: product framing, pricing tiers, integrations advertised.
2. Find the SDK/API (REST? MCP server? Browser extension? CC plugin?). Identify ingestion path — does it record conversations from Claude Code automatically, or only on demand?
3. Verbatim vs. summarized: confirm "recall verbatim conversations" claim (Level 4) — is the storage lossless?
4. Privacy posture: where does data go? Encryption? Multi-tenant model?
5. Performance numbers: any published latency/recall figures? Mark as `unknown` if absent.
6. Lock-in: data export options.

## Output

- **Findings:** `findings/06-recall-it.md` — DIMENSIONS table + ≤ 800 words.
- **Notes:** `3rd-party/notes/recall-it.md` — ≤ 200 words.
- **Format:** see DIMENSIONS.md.

## INDEX.md row to add

```
| Recall.it | https://www.recall.it/ | n/a (hosted SaaS) | Claude Code Memory Systems Survey | notes-only | 2026-04-25 | Level 4 — verbatim conversation recall |
```
