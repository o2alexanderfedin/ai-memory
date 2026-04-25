"""POST /personas + GET /personas happy-path tests."""
from fastapi import status
from fastapi.testclient import TestClient

from ai_hive_memory.main import app

client = TestClient(app)


def _signup() -> str:
    """Sign up a new tenant and return the bearer token."""
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_post_personas_creates_persona_and_returns_ulid() -> None:
    token = _signup()
    resp = client.post("/personas", headers=_auth(token))
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert "persona_id" in body
    assert len(body["persona_id"]) == 26  # ULID  # noqa: PLR2004


def test_get_personas_returns_empty_for_new_tenant() -> None:
    token = _signup()
    resp = client.get("/personas", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"personas": []}


def test_get_personas_returns_created_persona() -> None:
    token = _signup()
    create_resp = client.post("/personas", headers=_auth(token))
    persona_id = create_resp.json()["persona_id"]

    list_resp = client.get("/personas", headers=_auth(token))
    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.json() == {"personas": [persona_id]}


def test_post_personas_unauthenticated_returns_401() -> None:
    resp = client.post("/personas")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_personas_unauthenticated_returns_401() -> None:
    resp = client.get("/personas")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
