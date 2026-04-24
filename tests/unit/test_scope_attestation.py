"""ScopeAttestation Pydantic model tests (Decision 12 MVP customer-scope exclusions)."""
import pytest
from pydantic import ValidationError

from ai_hive_memory.auth.scope_attestation import ScopeAttestation


def _all_true() -> dict[str, bool]:
    return {
        "no_phi": True,
        "no_payment_data": True,
        "no_minors": True,
        "no_eu_uk_residents": True,
        "no_sensitive_categories": True,
    }


def test_all_true_attestation_validates() -> None:
    att = ScopeAttestation.model_validate(_all_true())
    assert att.no_phi is True


def test_any_false_attestation_rejected() -> None:
    """Each scope-exclusion must be explicitly attested True (Decision 12)."""
    for field in ["no_phi", "no_payment_data", "no_minors",
                  "no_eu_uk_residents", "no_sensitive_categories"]:
        bad = _all_true() | {field: False}
        with pytest.raises(ValidationError):
            ScopeAttestation.model_validate(bad)


def test_missing_field_rejected() -> None:
    """All 5 attestations are required — missing one is an error."""
    bad = _all_true()
    del bad["no_phi"]
    with pytest.raises(ValidationError):
        ScopeAttestation.model_validate(bad)


def test_extra_field_rejected() -> None:
    """Closed schema — extra fields rejected (DIR-1.1 spirit applied to API DTOs)."""
    bad = _all_true() | {"unexpected_field": True}
    with pytest.raises(ValidationError):
        ScopeAttestation.model_validate(bad)
