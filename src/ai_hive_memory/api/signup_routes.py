"""POST /signup — create a new tenant + record scope attestations + return JWT."""
from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text

from ai_hive_memory.auth.geoip import (
    BlockedCountryError,
    DefaultIPGeoBlocker,
)
from ai_hive_memory.auth.jwt import issue_token
from ai_hive_memory.auth.scope_attestation import ScopeAttestation
from ai_hive_memory.storage.db import get_engine
from ai_hive_memory.storage.rls import tenant_scope

router = APIRouter()

_BLOCKED_COUNTRIES = frozenset({
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE", "GB",
})

_geo_blocker = DefaultIPGeoBlocker()


class SignupRequest(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")

    subject: str
    tos_version: str
    scope_attestation: ScopeAttestation


class SignupResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")

    access_token: str
    tenant_id: str
    token_type: str = "bearer"


@router.post("/signup")
def signup(
    req: SignupRequest,
    request: Request,
    x_forwarded_for: str | None = Header(default=None),
) -> SignupResponse:
    source_ip = (x_forwarded_for or "").split(",")[0].strip() or (
        request.client.host if request.client else ""
    )
    source_country = _geo_blocker.lookup_country(source_ip) if source_ip else None
    try:
        _geo_blocker.assert_not_blocked(source_ip, set(_BLOCKED_COUNTRIES))
    except BlockedCountryError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    tenant_id = str(uuid4())

    with get_engine().begin() as conn, tenant_scope(conn, tenant_id):
        conn.execute(
            text("INSERT INTO tenants (tenant_id, tos_version) VALUES (:tid, :tos)"),
            {"tid": tenant_id, "tos": req.tos_version},
        )
        conn.execute(
            text("""
                INSERT INTO scope_attestations
                  (tenant_id, no_phi, no_payment_data, no_minors,
                   no_eu_uk_residents, no_sensitive_categories,
                   source_ip, source_country)
                VALUES
                  (:tid, :phi, :pay, :min, :eu, :sens, :ip, :country)
            """),
            {
                "tid": tenant_id,
                "phi": req.scope_attestation.no_phi,
                "pay": req.scope_attestation.no_payment_data,
                "min": req.scope_attestation.no_minors,
                "eu": req.scope_attestation.no_eu_uk_residents,
                "sens": req.scope_attestation.no_sensitive_categories,
                "ip": source_ip or None,
                "country": source_country,
            },
        )

    token = issue_token(
        tenant_id=tenant_id,
        subject=req.subject,
        expires_in=timedelta(hours=8),
    )
    return SignupResponse(access_token=token, tenant_id=tenant_id)
