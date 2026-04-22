"""Auth endpoints — at MVP, simple developer-issued token."""
from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from synthius_mem.auth.jwt import issue_token

router = APIRouter()


class TokenRequest(BaseModel):  # type: ignore[explicit-any]
    subject: str
    tenant_id: str | None = None  # if None, we mint a new tenant


class TokenResponse(BaseModel):  # type: ignore[explicit-any]
    access_token: str
    tenant_id: str
    token_type: str = "bearer"


@router.post("/auth/token")
def mint_token(req: TokenRequest) -> TokenResponse:
    """MVP: developer-issued token. Replace with real OAuth2 IdP in Phase 7."""
    tenant_id = req.tenant_id or str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject=req.subject,
                        expires_in=timedelta(hours=8))
    return TokenResponse(access_token=token, tenant_id=tenant_id)
