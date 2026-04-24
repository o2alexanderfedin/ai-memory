"""Root landing page — service description, API docs links, live health widget."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>__TITLE__ v__VERSION__</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --fg: #1f2328; --muted: #656d76; --accent: #0969da; --bg: #ffffff;
      --panel: #f6f8fa; --border: #d0d7de;
      --ok: #1a7f37; --ok-bg: #dafbe1;
      --warn: #9a6700; --warn-bg: #fff8c5;
      --err: #cf222e; --err-bg: #ffebe9;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --fg: #e6edf3; --muted: #8b949e; --accent: #58a6ff; --bg: #0d1117;
        --panel: #161b22; --border: #30363d;
        --ok: #3fb950; --ok-bg: #0f2a17;
        --warn: #d29922; --warn-bg: #2d230a;
        --err: #f85149; --err-bg: #301012;
      }
    }
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      color: var(--fg); background: var(--bg); margin: 0; line-height: 1.55;
    }
    main { max-width: 720px; margin: 0 auto; padding: 3rem 1.5rem; }
    h1 { margin: 0 0 0.25rem; font-size: 1.9rem; }
    .version { color: var(--muted); font-size: 0.95rem; margin-bottom: 1.5rem; }
    p.lede { font-size: 1.05rem; color: var(--fg); }
    h2 { font-size: 1.1rem; margin-top: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.35rem; }
    ul.links { list-style: none; padding: 0; }
    ul.links li { margin: 0.4rem 0; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .endpoint { display: inline-block; min-width: 9.5rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }

    .health-card {
      display: flex; align-items: center; gap: 0.9rem;
      padding: 0.9rem 1rem; border-radius: 8px;
      border: 1px solid var(--border); background: var(--panel);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }
    .health-dot {
      width: 0.8rem; height: 0.8rem; border-radius: 50%;
      background: var(--muted); flex-shrink: 0;
      box-shadow: 0 0 0 0 rgba(0,0,0,0);
    }
    .health-card--ok   { background: var(--ok-bg);   border-color: var(--ok); }
    .health-card--ok   .health-dot { background: var(--ok); animation: pulse 2s ease-in-out infinite; }
    .health-card--warn { background: var(--warn-bg); border-color: var(--warn); }
    .health-card--warn .health-dot { background: var(--warn); }
    .health-card--err  { background: var(--err-bg);  border-color: var(--err); }
    .health-card--err  .health-dot { background: var(--err); }
    @keyframes pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(63,185,80,0.45); }
      50%      { box-shadow: 0 0 0 6px rgba(63,185,80,0); }
    }
    .health-body { flex: 1; min-width: 0; }
    .health-label { font-weight: 600; font-size: 0.95rem; }
    .health-meta  { color: var(--muted); font-size: 0.82rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin-top: 0.15rem; word-break: break-all; }

    footer { margin-top: 3rem; color: var(--muted); font-size: 0.85rem; }
  </style>
</head>
<body>
  <main>
    <h1>__TITLE__</h1>
    <div class="version">v__VERSION__</div>

    <p class="lede">
      A persona-scoped long-term memory service for LLM agents &mdash; stores, retrieves,
      and attests to structured memories across tenants with Postgres row-level security
      and pluggable LLM backends (GLM, Anthropic, z.ai) via LiteLLM.
    </p>

    <h2>API Documentation</h2>
    <ul class="links">
      <li><span class="endpoint">Swagger UI</span> <a href="/docs">/docs</a> &mdash; interactive try-it-out console</li>
      <li><span class="endpoint">ReDoc</span> <a href="/redoc">/redoc</a> &mdash; reference-style reading view</li>
      <li><span class="endpoint">OpenAPI schema</span> <a href="/openapi.json">/openapi.json</a> &mdash; machine-readable contract</li>
    </ul>

    <h2>Service Health</h2>
    <div id="health-status" class="health-card" role="status" aria-live="polite">
      <div class="health-dot" aria-hidden="true"></div>
      <div class="health-body">
        <div class="health-label">Checking&hellip;</div>
        <div class="health-meta">Polling <code>/health</code> every 5s</div>
      </div>
    </div>

    <footer>AI Hive&reg; Memory &middot; FastAPI + Postgres + LiteLLM</footer>
  </main>

  <script>
    (function () {
      var card  = document.getElementById('health-status');
      var label = card.querySelector('.health-label');
      var meta  = card.querySelector('.health-meta');

      function setState(cls, labelText, metaText) {
        card.className = 'health-card ' + cls;
        label.textContent = labelText;
        meta.textContent  = metaText;
      }

      async function check() {
        var started = performance.now();
        try {
          var res = await fetch('/health', { cache: 'no-store' });
          var latency = Math.round(performance.now() - started);
          if (!res.ok) {
            setState('health-card--err', 'HTTP ' + res.status, 'Polling /health every 5s · ' + latency + 'ms');
            return;
          }
          var data = await res.json();
          var statusText = (data.status || 'unknown').toString().toUpperCase();
          var cls = statusText === 'OK' ? 'health-card--ok' : 'health-card--warn';
          setState(cls, statusText + ' · ' + latency + 'ms', (data.timestamp || '') + ' · every 5s');
        } catch (err) {
          setState('health-card--err', 'UNREACHABLE', (err && err.message ? err.message : String(err)) + ' · retry in 5s');
        }
      }

      check();
      setInterval(check, 5000);
    })();
  </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request) -> HTMLResponse:
    app = request.app
    html = _PAGE.replace("__TITLE__", app.title).replace("__VERSION__", app.version)
    return HTMLResponse(html)
