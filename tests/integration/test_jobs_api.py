"""GET /jobs/{id} — job status polling (US-2.8)."""
import json
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from job_completion import WaitDone

from ai_hive_memory.main import app


def _signup(client: TestClient) -> str:
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    return resp.json()["access_token"]


def _create_persona(client: TestClient, token: str) -> str:
    resp = client.post("/personas", headers={"Authorization": f"Bearer {token}"})
    return resp.json()["persona_id"]


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_get_job_returns_status_and_per_domain_progress(
    mock_gw_cls: object, wait_done: WaitDone,
) -> None:
    instance = mock_gw_cls.return_value  # type: ignore[union-attr]
    instance.complete.return_value = json.dumps({})
    with TestClient(app) as client:
        token = _signup(client)
        persona_id = _create_persona(client, token)
        resp = client.post(
            f"/personas/{persona_id}/conversations",
            headers={"Authorization": f"Bearer {token}"},
            json={"format": "whatsapp", "content": "[2026-04-21 12:00] Alice: hi\n"},
        )
        job_id = resp.json()["job_id"]
        wait_done(client, token, job_id)
        get_resp = client.get(f"/jobs/{job_id}",
                              headers={"Authorization": f"Bearer {token}"})
        assert get_resp.status_code == status.HTTP_200_OK
        body = get_resp.json()
        assert body["status"] == "DONE"
        assert "domain_status" in body
        assert set(body["domain_status"].keys()) == {
            "biography", "experiences", "preferences",
            "social_circle", "work", "psychometrics",
        }


def test_get_unknown_job_returns_404() -> None:
    with TestClient(app) as client:
        token = _signup(client)
        resp = client.get(
            "/jobs/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_job_unauthenticated_returns_401() -> None:
    with TestClient(app) as client:
        resp = client.get("/jobs/any-id")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_job_with_malformed_id_returns_404() -> None:
    """A job id that is not a UUID names no job: 404, like any unknown job id."""
    with TestClient(app, raise_server_exceptions=False) as client:
        token = _signup(client)
        resp = client.get(
            "/jobs/not-a-uuid",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND, (
            f"GET /jobs/not-a-uuid answered {resp.status_code}: {resp.text}"
        )
