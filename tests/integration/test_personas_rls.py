"""LOAD-BEARING: prove /personas API enforces cross-tenant isolation (DIR-11.1).

This is the HTTP-layer counterpart to Epic 0 Task 9's SQL-layer RLS isolation
test. If this test ever fails, do NOT ship — one bug = total cross-tenant
data breach via the API.
"""
from fastapi import status
from fastapi.testclient import TestClient

from ai_hive_memory.main import app

client = TestClient(app)


def _signup() -> tuple[str, str]:
    """Returns (token, tenant_id) for a new tenant."""
    resp = client.post("/signup", json={
        "subject": "u@test",
        "tos_version": "2026-04-21-mvp",
        "scope_attestation": {
            "no_phi": True, "no_payment_data": True, "no_minors": True,
            "no_eu_uk_residents": True, "no_sensitive_categories": True,
        },
    })
    body = resp.json()
    return body["access_token"], body["tenant_id"]


def test_tenant_a_cannot_see_tenant_b_personas_via_api() -> None:
    token_a, tenant_a = _signup()
    token_b, tenant_b = _signup()
    assert tenant_a != tenant_b

    created_b = []
    for _ in range(3):
        resp = client.post("/personas", headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == status.HTTP_201_CREATED
        created_b.append(resp.json()["persona_id"])

    resp_a = client.get("/personas", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == status.HTTP_200_OK
    visible_to_a = set(resp_a.json()["personas"])
    leaked = visible_to_a & set(created_b)
    assert leaked == set(), f"RLS BREACH at API layer: tenant_a saw tenant_b personas: {leaked}"

    resp_b = client.get("/personas", headers={"Authorization": f"Bearer {token_b}"})
    assert set(resp_b.json()["personas"]) == set(created_b)
