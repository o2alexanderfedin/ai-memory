# recall-it (Recall / getRecall.ai)

- **Upstream:** https://www.recall.it/ — hosted SaaS, no clone.
- **Vendor:** Recall, Amsterdam NL. Founders Paul Richards (CEO),
  Igor Gligorevic (CTO), Sankari Nair (COO). Founded Nov 2022 from a
  Hacker News post; $1.5M seed Dec 2024 (Jason Calacanis lead).
- **What it is:** A "personal second brain." Browser extension + web/
  mobile app for saving articles, PDFs, podcasts, YouTube, notes —
  each becomes a *card* with AI summary, tags, and graph connections.
  Recall 2.0 (14 Apr 2026) added an MCP server.
- **Claude Code surface:** MCP at `https://backend.getrecall.ai/mcp/`,
  OAuth (scope `kb:read`), four read-only tools: `search`,
  `filter_by_metadata`, `get_document_content`, `explore_kb`.
  REST API at `…/api/v1` is also read-only (Bearer `sk_…`).
  **No write API yet** — "coming soon."
- **Storage:** GCP `europe-west1` (Belgium), local-first device cache.
  Markdown export of full KB available; lock-in is low.
- **Pricing:** Free (10 AI cards/mo) · Plus $10/mo · Max $38/mo (yearly).
- **Caveat on the survey's Level-4 tag:** The "verbatim conversation
  recall" label fits poorly. Recall stores *user-curated source
  content*, not Claude Code chat turns. Likely confusion with the
  unrelated Recall.ai (YC, meeting transcripts API). Detail in the
  findings file.
- **Findings:** `notes/cc-memory-systems-survey/findings/06-recall-it.md`.
