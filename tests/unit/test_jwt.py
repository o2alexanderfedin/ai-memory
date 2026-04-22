"""Tests for JWT issuer/verifier (DIR-7.3)."""
from datetime import timedelta
from uuid import uuid4

import pytest
from jose import JWTError

from synthius_mem.auth.jwt import TokenClaims, issue_token, verify_token


def test_issue_and_verify_round_trip() -> None:
    tenant_id = str(uuid4())
    subject = "user@example.com"
    token = issue_token(tenant_id=tenant_id, subject=subject, expires_in=timedelta(minutes=15))
    claims = verify_token(token)
    assert claims.tenant_id == tenant_id
    assert claims.sub == subject


def test_expired_token_raises() -> None:
    tenant_id = str(uuid4())
    token = issue_token(tenant_id=tenant_id, subject="x", expires_in=timedelta(seconds=-1))
    with pytest.raises(JWTError):
        verify_token(token)


def test_tampered_token_raises() -> None:
    token = issue_token(tenant_id=str(uuid4()), subject="x", expires_in=timedelta(minutes=5))
    tampered = token[:-3] + "XYZ"
    with pytest.raises(JWTError):
        verify_token(tampered)


def test_token_claims_pydantic_validation() -> None:
    """tenant_id MUST be UUID format."""
    with pytest.raises(ValueError):
        TokenClaims(sub="x", tenant_id="not-a-uuid", exp=9999999999)
