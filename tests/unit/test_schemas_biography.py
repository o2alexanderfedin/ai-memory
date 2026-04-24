"""Tests for Biography domain schema (DIR-1.1, DIR-1.8)."""
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from ulid import ULID

from ai_hive_memory.schemas.biography import Biography, BiographyFields, DatePrecision
from ai_hive_memory.schemas.envelope import CommonEnvelope, Provenance


def _envelope() -> CommonEnvelope:
    return CommonEnvelope(
        persona_id=str(ULID()),
        domain="biography",
        schema_version="1.0.0",
        confidence=0.9,
        provenance=Provenance(
            source_message_id=str(ULID()),
            source_chunk_id=str(ULID()),
            extracted_at=datetime.now(UTC),
            extractor_version="test",
        ),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _biography_fields() -> dict[str, Any]:
    """DIR-1.8: typed sub-fields, ISO-8601 + precision marker."""
    return {
        "place_of_birth": {"_raw": "London", "_ref": None},
        "birth_date": "1990-06-15",
        "birth_date_precision": "day",
        "education": [
            {
                "degree": "PhD",
                "field": "Neuroscience",
                "institution": {"_raw": "UCL", "_ref": None},
                "year": 2019,
            }
        ],
    }


def test_biography_round_trip() -> None:
    bio = Biography(envelope=_envelope(), fields=BiographyFields(**_biography_fields()))
    serialized = bio.model_dump(mode="json")
    rebuilt = Biography.model_validate(serialized)
    assert rebuilt == bio


def test_biography_rejects_extra_fields() -> None:
    """DIR-1.1: additionalProperties: false."""
    bad = _biography_fields() | {"unexpected": "rejected"}
    with pytest.raises(ValidationError):
        BiographyFields.model_validate(bad)


def test_biography_date_precision_enum() -> None:
    """DIR-1.8: precision must be year|month|day."""
    assert {p.value for p in DatePrecision} == {"year", "month", "day"}


def test_biography_emits_json_schema() -> None:
    """Schema must be exportable for downstream prompt generation."""
    schema = Biography.model_json_schema()
    assert schema["additionalProperties"] is False
    # The fields sub-schema must also be closed
    fields_schema = schema["$defs"]["BiographyFields"]
    assert fields_schema["additionalProperties"] is False
