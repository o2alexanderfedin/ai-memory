"""LOAD-BEARING: tenant_a cannot read tenant_b's ingest_jobs or pending_facts (DIR-11.1)."""
import json
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from job_completion import WaitDone

from ai_hive_memory.main import app

client = TestClient(app)


def _signup() -> str:
    return client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    }).json()["access_token"]


def _persona(token: str) -> str:
    return client.post("/personas",
                       headers={"Authorization": f"Bearer {token}"}).json()["persona_id"]


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_tenant_a_cannot_read_tenant_b_jobs_via_api(
    mock_gw_cls: object, wait_done: WaitDone,
) -> None:
    mock_gw_cls.return_value.complete.return_value = json.dumps({})  # type: ignore[union-attr]

    token_a = _signup()
    token_b = _signup()
    persona_b = _persona(token_b)

    # tenant_b creates an ingest job
    r = client.post(
        f"/personas/{persona_b}/conversations",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"format": "whatsapp", "content": "[2026-04-21 12:00] B: hi\n"},
    )
    job_b = r.json()["job_id"]
    wait_done(client, token_b, job_b)

    # tenant_a tries to read tenant_b's job — must be 404
    resp_a = client.get(f"/jobs/{job_b}",
                        headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == status.HTTP_404_NOT_FOUND, (
        f"RLS BREACH: tenant_a saw tenant_b's job {job_b}"
    )

    # Sanity: tenant_b can read it
    resp_b = client.get(f"/jobs/{job_b}",
                        headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == status.HTTP_200_OK


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_tenant_a_cannot_post_conversation_against_tenant_b_persona(
    mock_gw_cls: object,
) -> None:
    mock_gw_cls.return_value.complete.return_value = json.dumps({})  # type: ignore[union-attr]
    token_a = _signup()
    token_b = _signup()
    persona_b = _persona(token_b)

    # tenant_a tries to POST against persona that belongs to tenant_b — must 404
    resp = client.post(
        f"/personas/{persona_b}/conversations",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"format": "whatsapp", "content": "x"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
