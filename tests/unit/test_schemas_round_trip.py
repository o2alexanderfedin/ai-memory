"""Cross-domain round-trip + closed-schema check (DIR-1.1, DIR-1.3)."""
from datetime import datetime, timezone

import pytest
from ulid import ULID

from synthius_mem.schemas.biography import Biography, BiographyFields
from synthius_mem.schemas.envelope import CommonEnvelope, Provenance
from synthius_mem.schemas.experiences import Experiences, ExperiencesFields
from synthius_mem.schemas.preferences import Preferences, PreferencesFields
from synthius_mem.schemas.psychometrics import Psychometrics, PsychometricsFields
from synthius_mem.schemas.social_circle import SocialCircle, SocialCircleFields
from synthius_mem.schemas.work import Work, WorkFields


def _make_envelope(domain: str) -> CommonEnvelope:
    now = datetime.now(timezone.utc)
    return CommonEnvelope(
        persona_id=str(ULID()),
        domain=domain,
        schema_version="1.0.0",
        confidence=0.5,
        provenance=Provenance(
            source_message_id=str(ULID()),
            source_chunk_id=str(ULID()),
            extracted_at=now,
            extractor_version="test",
        ),
        created_at=now,
        updated_at=now,
    )


@pytest.mark.parametrize(
    "fact_cls,fields_cls,domain",
    [
        (Biography, BiographyFields, "biography"),
        (Experiences, ExperiencesFields, "experiences"),
        (Preferences, PreferencesFields, "preferences"),
        (SocialCircle, SocialCircleFields, "social_circle"),
        (Work, WorkFields, "work"),
        (Psychometrics, PsychometricsFields, "psychometrics"),
    ],
)
def test_each_domain_round_trips(fact_cls, fields_cls, domain: str) -> None:
    fact = fact_cls(envelope=_make_envelope(domain), fields=fields_cls())
    rebuilt = fact_cls.model_validate(fact.model_dump(mode="json"))
    assert rebuilt == fact


@pytest.mark.parametrize(
    "fact_cls",
    [Biography, Experiences, Preferences, SocialCircle, Work, Psychometrics],
)
def test_each_domain_schema_is_closed(fact_cls) -> None:
    """DIR-1.1: every domain top-level + its fields must reject extras."""
    schema = fact_cls.model_json_schema()
    assert schema["additionalProperties"] is False
