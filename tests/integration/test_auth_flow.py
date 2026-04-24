"""End-to-end auth flow + RLS context propagation."""
from datetime import timedelta
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from ai_hive_memory.auth.jwt import issue_token
from ai_hive_memory.main import app

client = TestClient(app)


def test_unauthenticated_request_to_protected_endpoint_returns_401() -> None:
    resp = client.get("/personas")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_valid_token_allows_access() -> None:
    tenant_id = str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject="t@example.com",
                        expires_in=timedelta(minutes=5))
    resp = client.get("/personas", headers={"Authorization": f"Bearer {token}"})
    # 200 or 404 acceptable; what matters: NOT 401
    assert resp.status_code != status.HTTP_401_UNAUTHORIZED


def test_invalid_token_returns_401() -> None:
    resp = client.get("/personas",
                      headers={"Authorization": "Bearer not.a.token"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_token_requires_existing_tenant_id() -> None:
    resp = client.post("/auth/token", json={
        "subject": "x@test",
        "tenant_id": str(uuid4()),
    })
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_auth_token_works_for_existing_tenant() -> None:
    signup_resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    tenant_id = signup_resp.json()["tenant_id"]

    resp = client.post("/auth/token", json={
        "subject": "u@test",
        "tenant_id": tenant_id,
    })
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["tenant_id"] == tenant_id


def test_auth_token_without_tenant_id_returns_422() -> None:
    """tenant_id is now mandatory (no anonymous minting)."""
    resp = client.post("/auth/token", json={"subject": "u@test"})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
