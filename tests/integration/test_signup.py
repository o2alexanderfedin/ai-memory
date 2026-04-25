"""POST /signup — tenant creation + scope attestation + JWT issuance."""
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text

from ai_hive_memory.main import app
from ai_hive_memory.storage.db import get_engine
from ai_hive_memory.storage.rls import tenant_scope

client = TestClient(app)


def _valid_signup() -> dict:
    return {
        "subject": "alice@example.com",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True,
            "no_payment_data": True,
            "no_minors": True,
            "no_eu_uk_residents": True,
            "no_sensitive_categories": True,
        },
    }


def test_signup_with_valid_attestations_returns_jwt_and_tenant_id() -> None:
    resp = client.post("/signup", json=_valid_signup())
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "access_token" in body
    assert "tenant_id" in body
    assert body["token_type"] == "bearer"


def test_signup_with_false_attestation_rejected_422() -> None:
    body = _valid_signup()
    body["scope_attestation"]["no_phi"] = False
    resp = client.post("/signup", json=body)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_with_missing_attestation_rejected_422() -> None:
    body = _valid_signup()
    del body["scope_attestation"]["no_phi"]
    resp = client.post("/signup", json=body)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_records_tenant_and_attestation_in_db() -> None:
    """After signup, tenant + scope_attestations rows exist for the new tenant."""
    resp = client.post("/signup", json=_valid_signup())
    assert resp.status_code == status.HTTP_200_OK
    tenant_id = resp.json()["tenant_id"]

    with get_engine().begin() as conn, tenant_scope(conn, tenant_id):
        tenant_row = conn.execute(
            text("SELECT tos_version FROM tenants WHERE tenant_id = :tid"),
            {"tid": tenant_id},
        ).fetchone()
        assert tenant_row is not None
        assert tenant_row[0] == "2026-04-21-mvp"

        att_row = conn.execute(
            text("""
                SELECT no_phi, no_payment_data, no_minors,
                       no_eu_uk_residents, no_sensitive_categories
                FROM scope_attestations WHERE tenant_id = :tid
            """),
            {"tid": tenant_id},
        ).fetchone()
        assert att_row is not None
        assert all(att_row)  # all 5 must be True
