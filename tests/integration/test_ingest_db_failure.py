"""A database error during ingest must end the job as FAILED, never leave it PENDING."""
import json
from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from job_completion import WaitEnded
from sqlalchemy import text
from sqlalchemy.engine import Connection

from ai_hive_memory.auth.jwt import verify_token
from ai_hive_memory.ingest.pipeline import DOMAINS
from ai_hive_memory.main import app
from ai_hive_memory.storage.connection import request_scoped_conn
from ai_hive_memory.storage.ingest_repository import PendingFactRepository

# The pipeline's exception must not be re-raised into the POST call: the
# client gets its 202 before the job runs, as in production.
client = TestClient(app, raise_server_exceptions=False)


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


def _upload(token: str, content: str) -> str:
    auth = {"Authorization": f"Bearer {token}"}
    persona_id = client.post("/personas", headers=auth).json()["persona_id"]
    r = client.post(f"/personas/{persona_id}/conversations", headers=auth,
                    json={"format": "whatsapp", "content": content})
    assert r.status_code == status.HTTP_202_ACCEPTED
    job_id: str = r.json()["job_id"]
    return job_id


def _bio_only(*, tier: object, messages: list[dict[str, str]], json_mode: bool,
              temperature: float = 0.0, max_tokens: int = 2048) -> str:
    if "biographical" in messages[0]["content"].lower():
        return json.dumps({"birth_date_precision": "year"})
    return json.dumps({})


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_message_with_nul_character_is_ingested(
    mock_gw_cls: MagicMock, wait_ended: WaitEnded,
) -> None:
    """Postgres jsonb rejects \\u0000; the NUL must be removed, not fail the job."""
    mock_gw_cls.return_value.complete.side_effect = _bio_only
    token = _signup()
    job_id = _upload(token, "[2026-04-21 12:00] Alice: I was born\x00 in 1990.\n")
    body = wait_ended(client, token, job_id)
    assert body["status"] == "DONE", f"job ended as {body['status']}: {body['error']}"
    assert body["domain_status"] == dict.fromkeys(DOMAINS, "DONE"), (
        f"storing a fact that contains NUL failed: {body['domain_status']}"
    )

    tenant_id = verify_token(token).tenant_id
    gen = request_scoped_conn(tenant_id)
    conn = next(gen)
    try:
        facts = PendingFactRepository().list_for_job(conn, tenant_id, job_id)
    finally:
        gen.close()
    assert len(facts) == 1, f"expected the biography fact, got {len(facts)}"
    stored = json.dumps(facts[0]["payload"], ensure_ascii=False)
    assert "\x00" not in stored
    assert "I was born in 1990." in stored, "the message text around the NUL must be kept"


def _broken_db_call(self: PendingFactRepository, conn: Connection, *a: object,
                    **kw: object) -> None:
    conn.execute(text("SELECT 1 / 0"))  # any database error aborts the transaction


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_database_error_during_ingest_marks_job_failed(
    mock_gw_cls: MagicMock, wait_ended: WaitEnded,
) -> None:
    mock_gw_cls.return_value.complete.side_effect = _bio_only
    token = _signup()
    with patch.object(PendingFactRepository, "mark_seen", _broken_db_call):
        job_id = _upload(token, "[2026-04-21 12:00] Alice: I was born in 1990.\n")
    body = wait_ended(client, token, job_id)
    assert body["status"] == "FAILED", (
        f"after a database error the job must be FAILED, but it is {body['status']}"
    )
    assert str(body["error"]).startswith("(psycopg.errors.DivisionByZero)"), (
        f"the job's error must be the database error itself, not a later one; "
        f"it is {body['error']!r}"
    )


@patch("ai_hive_memory.api.conversations.LLMGateway")
def test_database_error_storing_one_domain_keeps_the_other_domains(
    mock_gw_cls: MagicMock, wait_ended: WaitEnded,
) -> None:
    """Storing the biography fact fails; the other five domains still count (5/6 accept)."""
    mock_gw_cls.return_value.complete.side_effect = _bio_only
    token = _signup()
    with patch.object(PendingFactRepository, "persist", _broken_db_call):
        job_id = _upload(token, "[2026-04-21 12:00] Alice: I was born in 1990.\n")
    body = wait_ended(client, token, job_id)
    assert body["status"] == "DONE", (
        f"a database error in one domain must not fail the job; "
        f"it ended as {body['status']}: {body['error']}"
    )
    domain_status = body["domain_status"]
    assert isinstance(domain_status, dict)
    assert "division by zero" in domain_status["biography"], domain_status
    others = {d: v for d, v in domain_status.items() if d != "biography"}
    assert set(others.values()) == {"DONE"}, domain_status
