"""Auth endpoints — at MVP, simple token-mint for EXISTING tenants only.

Tenant creation is exclusively via /signup (which records scope attestations).
This endpoint cannot create tenants — only re-issue tokens for tenants that
already attested at signup. Phase 7: replace with real OAuth2 IdP.
"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text

from ai_hive_memory.auth.jwt import issue_token
from ai_hive_memory.storage.db import get_engine
from ai_hive_memory.storage.rls import tenant_scope

router = APIRouter()


class TokenRequest(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    subject: str
    tenant_id: str  # MANDATORY — no anonymous minting


class TokenResponse(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")
    access_token: str
    tenant_id: str
    token_type: str = "bearer"


@router.post("/auth/token")
def mint_token(req: TokenRequest) -> TokenResponse:
    """Issue a token for an EXISTING tenant. Use /signup to create tenants."""
    with get_engine().begin() as conn, tenant_scope(conn, req.tenant_id):
        row = conn.execute(
            text("SELECT 1 FROM tenants WHERE tenant_id = :tid"),
            {"tid": req.tenant_id},
        ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found; use /signup")

    token = issue_token(
        tenant_id=req.tenant_id,
        subject=req.subject,
        expires_in=timedelta(hours=8),
    )
    return TokenResponse(access_token=token, tenant_id=req.tenant_id)
