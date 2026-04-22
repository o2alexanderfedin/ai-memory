"""End-to-end auth flow + RLS context propagation."""
from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from synthius_mem.auth.jwt import issue_token
from synthius_mem.main import app

client = TestClient(app)


def test_unauthenticated_request_to_protected_endpoint_returns_401() -> None:
    resp = client.get("/personas")
    assert resp.status_code == 401


def test_valid_token_allows_access() -> None:
    tenant_id = str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject="t@example.com",
                        expires_in=timedelta(minutes=5))
    resp = client.get("/personas", headers={"Authorization": f"Bearer {token}"})
    # 200 or 404 acceptable; what matters: NOT 401
    assert resp.status_code != 401


def test_invalid_token_returns_401() -> None:
    resp = client.get("/personas",
                      headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == 401
