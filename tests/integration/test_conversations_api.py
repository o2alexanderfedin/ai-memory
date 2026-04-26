"""POST /personas/{id}/conversations — upload + async job kickoff."""
import json
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from ai_hive_memory.main import app

client = TestClient(app)


def _signup() -> str:
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    return resp.json()["access_token"]


def _create_persona(token: str) -> str:
    resp = client.post("/personas", headers={"Authorization": f"Bearer {token}"})
    return resp.json()["persona_id"]


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_post_conversation_returns_job_id_and_202(mock_gw_cls: object) -> None:
    instance = mock_gw_cls.return_value  # type: ignore[union-attr]
    instance.complete.return_value = json.dumps({})
    token = _signup()
    persona_id = _create_persona(token)
    resp = client.post(
        f"/personas/{persona_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"format": "whatsapp", "content": "[2026-04-21 12:00] Alice: hi\n"},
    )
    assert resp.status_code == status.HTTP_202_ACCEPTED
    assert "job_id" in resp.json()


def test_post_conversation_unauthenticated_returns_401() -> None:
    resp = client.post("/personas/anything/conversations", json={
        "format": "whatsapp", "content": "x",
    })
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_post_conversation_unknown_persona_returns_404() -> None:
    token = _signup()
    resp = client.post(
        "/personas/01J0000000000000000000XXXX/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"format": "whatsapp", "content": "x"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_post_conversation_unknown_format_returns_400() -> None:
    token = _signup()
    persona_id = _create_persona(token)
    resp = client.post(
        f"/personas/{persona_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"format": "made-up", "content": "x"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
