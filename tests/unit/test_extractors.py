"""Per-domain extractor classes — each calls LLMGateway, validates closed-schema response."""
import json
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from ai_hive_memory.ingest.chunker import Chunk
from ai_hive_memory.ingest.extractors.biography import BiographyExtractor
from ai_hive_memory.ingest.extractors.experiences import ExperiencesExtractor
from ai_hive_memory.ingest.extractors.preferences import PreferencesExtractor
from ai_hive_memory.ingest.extractors.psychometrics import PsychometricsExtractor
from ai_hive_memory.ingest.extractors.social_circle import SocialCircleExtractor
from ai_hive_memory.ingest.extractors.work import WorkExtractor
from ai_hive_memory.ingest.messages import Message
from ai_hive_memory.llm.models import ModelTier


def _chunk() -> Chunk:
    return Chunk(messages=(
        Message(
            speaker="Alice",
            timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
            text="I was born in Boston in 1990.",
        ),
    ), persona_id="01J0000000000000000000ABCD")


@pytest.mark.parametrize("extractor_cls,domain,fields_payload", [
    (BiographyExtractor, "biography", {"birth_date": "1990-01-01", "birth_date_precision": "year"}),
    (ExperiencesExtractor, "experiences", {"parent_event_id": None, "children": []}),
    (PreferencesExtractor, "preferences", {}),
    (SocialCircleExtractor, "social_circle", {"relations": []}),
    (WorkExtractor, "work", {}),
    (PsychometricsExtractor, "psychometrics", {}),
])
def test_extractor_calls_volume_tier_with_json_mode(
    extractor_cls: type, domain: str, fields_payload: dict[str, object],
) -> None:
    gw = MagicMock()
    gw.complete.return_value = json.dumps(fields_payload)
    extractor = extractor_cls(gateway=gw)
    facts = extractor.extract(_chunk())
    call_kwargs = gw.complete.call_args.kwargs
    assert call_kwargs["tier"] == ModelTier.VOLUME
    assert call_kwargs["json_mode"] is True
    assert isinstance(facts, list)
    for f in facts:
        assert f.envelope.domain == domain
        assert f.envelope.persona_id == "01J0000000000000000000ABCD"


def test_biography_extractor_rejects_extra_fields_in_response() -> None:
    gw = MagicMock()
    gw.complete.return_value = json.dumps({"birth_date": "1990-01-01", "rogue_field": "nope"})
    extractor = BiographyExtractor(gateway=gw)
    with pytest.raises(ValidationError):
        extractor.extract(_chunk())
