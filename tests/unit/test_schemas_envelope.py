"""Tests for the shared CommonEnvelope (DIR-1.3)."""
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from ulid import ULID

from ai_hive_memory.schemas.envelope import CommonEnvelope, Provenance


def _now() -> datetime:
    return datetime.now(UTC)


def _envelope_kwargs() -> dict:
    return dict(
        persona_id=str(ULID()),
        domain="biography",
        schema_version="1.0.0",
        confidence=0.85,
        provenance=Provenance(
            source_message_id=str(ULID()),
            source_chunk_id=str(ULID()),
            extracted_at=_now(),
            extractor_version="glm-4.7-flashx@2026-04-21",
        ),
        created_at=_now(),
        updated_at=_now(),
    )


def test_envelope_round_trip() -> None:
    env = CommonEnvelope(**_envelope_kwargs())
    serialized = env.model_dump(mode="json")
    rebuilt = CommonEnvelope.model_validate(serialized)
    assert rebuilt == env


def test_envelope_rejects_extra_fields() -> None:
    """DIR-1.1: closed schema — additionalProperties must be false."""
    bad = _envelope_kwargs() | {"unexpected_field": "should fail"}
    with pytest.raises(ValidationError):
        CommonEnvelope.model_validate(bad)


def test_envelope_confidence_in_unit_interval() -> None:
    """DIR-1.4: confidence is number in [0, 1]."""
    for bad_conf in [-0.1, 1.1, 1.5, -1]:
        with pytest.raises(ValidationError):
            CommonEnvelope.model_validate(_envelope_kwargs() | {"confidence": bad_conf})


def test_provenance_requires_extractor_version() -> None:
    """DIR-1.5: provenance MUST include extractor_version (T-044 rollback dep)."""
    base = _envelope_kwargs()
    bad_prov = base["provenance"].model_dump()
    del bad_prov["extractor_version"]
    with pytest.raises(ValidationError):
        Provenance.model_validate(bad_prov)
