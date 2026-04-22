"""FastAPI dependency: extract tenant from JWT, set RLS context."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError  # type: ignore[import-untyped]

from synthius_mem.auth.jwt import TokenClaims, verify_token


def require_auth(authorization: Annotated[str | None, Header()] = None) -> TokenClaims:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    token = authorization.removeprefix("Bearer ")
    try:
        return verify_token(token)
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"invalid token: {e}") from e


CurrentTenant = Annotated[TokenClaims, Depends(require_auth)]
