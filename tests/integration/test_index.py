"""Root index page — project description + links to Swagger/ReDoc."""
from fastapi import status
from fastapi.testclient import TestClient

from ai_hive_memory.main import app

client = TestClient(app)


def test_root_returns_html() -> None:
    resp = client.get("/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("text/html")


def test_root_links_to_swagger_redoc_and_openapi() -> None:
    body = client.get("/").text
    assert 'href="/docs"' in body
    assert 'href="/redoc"' in body
    assert 'href="/openapi.json"' in body


def test_root_shows_service_title_and_version() -> None:
    body = client.get("/").text
    assert app.title in body
    assert app.version in body


def test_root_has_live_health_widget_polling_every_5s() -> None:
    body = client.get("/").text
    # Widget container present.
    assert 'id="health-status"' in body
    # Polls the /health endpoint (not as a user-facing link).
    assert "/health" in body
    assert 'href="/health"' not in body
    # 5-second interval wired up via setInterval.
    assert "setInterval" in body
    assert "5000" in body
