"""US-2.3: re-uploading the same conversation yields 0 new pending_facts."""
import json
import time
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from ai_hive_memory.auth.jwt import verify_token
from ai_hive_memory.main import app
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.ingest_repository import PendingFactRepository

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
    token: str = resp.json()["access_token"]
    return token


def _persona(token: str) -> str:
    return client.post(
        "/personas",
        headers={"Authorization": f"Bearer {token}"},
    ).json()["persona_id"]


def _wait_done(token: str, job_id: str) -> None:
    for _ in range(40):
        body = client.get(
            f"/jobs/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        if body["status"] in {"DONE", "FAILED"}:
            return
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not finish")


def _tenant_from_token(token: str) -> str:
    return verify_token(token).tenant_id


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_re_upload_same_whatsapp_yields_zero_new_pending_facts(
    mock_gw_cls: object,
) -> None:
    """First upload produces facts; second (identical) upload produces zero."""
    payloads_by_systemkey: dict[str, dict[str, object]] = {
        "biographical": {"birth_date_precision": "year"},
        "life experiences": {"parent_event_id": None, "children": []},
        "stated preferences": {},
        "relationships": {"relations": []},
        "work-related": {},
        "psychometric": {},
    }

    def _complete(*, tier: object, messages: list[dict[str, str]],
                  json_mode: bool, temperature: float = 0.0,
                  max_tokens: int = 2048) -> str:
        sys_msg = messages[0]["content"].lower()
        for key, payload in payloads_by_systemkey.items():
            if key in sys_msg:
                return json.dumps(payload)
        return json.dumps({})

    mock_gw_cls.return_value.complete.side_effect = _complete  # type: ignore[union-attr]

    token = _signup()
    persona_id = _persona(token)
    raw_content = "[2026-04-21 12:00] Alice: I was born in 1990.\n"

    # First upload
    r1 = client.post(
        f"/personas/{persona_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"format": "whatsapp", "content": raw_content},
    )
    assert r1.status_code == status.HTTP_202_ACCEPTED
    job1 = r1.json()["job_id"]
    _wait_done(token, job1)

    # Second upload — identical content
    r2 = client.post(
        f"/personas/{persona_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"format": "whatsapp", "content": raw_content},
    )
    job2 = r2.json()["job_id"]
    _wait_done(token, job2)

    # Verify counts via DB
    tenant_id = _tenant_from_token(token)
    pf_repo = PendingFactRepository()
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        n1 = len(pf_repo.list_for_job(conn, tenant_id, job1))
        n2 = len(pf_repo.list_for_job(conn, tenant_id, job2))
        assert n1 > 0, "first upload must have produced facts"
        assert n2 == 0, f"second (duplicate) upload produced {n2} facts; expected 0"
    finally:
        gen.close()
