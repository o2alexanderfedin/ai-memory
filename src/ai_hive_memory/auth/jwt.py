"""JWT issuer/verifier (DIR-7.3 — OAuth2-compatible bearer tokens with tenant_id claim)."""
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import jwt  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, field_validator

from ai_hive_memory.config import get_settings

ALGORITHM = "HS256"


class TokenClaims(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="ignore")  # ignore standard JWT claims we don't validate

    sub: str
    tenant_id: str
    exp: int

    @field_validator("tenant_id")
    @classmethod
    def _tenant_id_is_uuid(cls, v: str) -> str:
        UUID(v)  # raises ValueError if not UUID-shaped
        return v


def issue_token(*, tenant_id: str, subject: str, expires_in: timedelta) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + expires_in
    to_encode = {
        "sub": subject,
        "tenant_id": tenant_id,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)  # type: ignore[no-any-return]


def verify_token(token: str) -> TokenClaims:
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    return TokenClaims.model_validate(payload)
