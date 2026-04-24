"""Health endpoint + OTel trace span emission."""
from fastapi import status
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ai_hive_memory.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["status"] == "ok"
    assert "timestamp" in body


def test_health_timestamp_is_iso8601_utc() -> None:
    from datetime import datetime, timezone

    resp = client.get("/health")
    ts = resp.json()["timestamp"]
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None
    # Must be UTC — offset zero.
    assert parsed.utcoffset() == timezone.utc.utcoffset(parsed)


def test_health_is_not_cached() -> None:
    resp = client.get("/health")
    cc = resp.headers.get("cache-control", "").lower()
    assert "no-store" in cc
    # Each call must produce a distinct timestamp (proves freshness, not caching).
    ts1 = resp.json()["timestamp"]
    ts2 = client.get("/health").json()["timestamp"]
    assert ts1 != ts2


def test_openapi_json_is_served() -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["info"]["title"] == "AI Hive® Memory"


def test_health_emits_otel_span() -> None:
    """Verify OTel tracer is instrumenting incoming requests (FastAPI auto-instr)."""
    exporter = InMemorySpanExporter()

    # Get the existing tracer provider that was set up in main.py
    existing_provider = trace.get_tracer_provider()
    if isinstance(existing_provider, TracerProvider):
        existing_provider.add_span_processor(SimpleSpanProcessor(exporter))
    else:
        # Fallback: if not a TracerProvider, create a new one and set it
        new_provider = TracerProvider()
        new_provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(new_provider)

    client.get("/health")

    spans = exporter.get_finished_spans()
    assert any(s.name.endswith("/health") or s.name == "GET" for s in spans), (
        f"No /health span emitted. Spans: {[s.name for s in spans]}"
    )
