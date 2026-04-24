"""ScopeAttestation — signup-time customer-scope exclusion record (Decision 12 MVP).

All five fields MUST be True for signup to proceed. If a tenant attests False
to any of them, signup is rejected (HTTP 422). This is the load-bearing
mechanism behind Decision 12's compliance scope reduction.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


def _must_be_true(value: bool, field_name: str) -> bool:
    if not value:
        raise ValueError(
            f"{field_name} must be True; signup blocked by Decision 12 scope exclusions"
        )
    return value


class ScopeAttestation(BaseModel):  # type: ignore[explicit-any]
    """Signup-time scope attestations. Each MUST be True (Decision 12)."""

    model_config = ConfigDict(extra="forbid")

    no_phi: Annotated[bool, Field(description="Will not ingest health/PHI data")]
    no_payment_data: Annotated[bool, Field(description="Will not ingest payment data")]
    no_minors: Annotated[bool, Field(description="Tenant is 18+ and will not ingest minors' data")]
    no_eu_uk_residents: Annotated[bool, Field(description="Tenant is not in EU/UK")]
    no_sensitive_categories: Annotated[
        bool, Field(description="Will not ingest GDPR Art. 9 sensitive categories")
    ]

    def model_post_init(self, __context: object) -> None:
        """Enforce all-True invariant after Pydantic validation."""
        for field_name in (
            "no_phi", "no_payment_data", "no_minors",
            "no_eu_uk_residents", "no_sensitive_categories",
        ):
            _must_be_true(getattr(self, field_name), field_name)
