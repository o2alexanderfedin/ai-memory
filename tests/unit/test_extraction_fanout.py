"""ExtractionFanout — concurrent per-domain extraction over a single chunk (US-2.6)."""
import json
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from ai_hive_memory.ingest.chunker import Chunk
from ai_hive_memory.ingest.extractors.base import ExtractionFanout
from ai_hive_memory.ingest.extractors.biography import BiographyExtractor
from ai_hive_memory.ingest.extractors.experiences import ExperiencesExtractor
from ai_hive_memory.ingest.messages import Message


def _chunk() -> Chunk:
    return Chunk(
        messages=(
            Message(
                speaker="Alice",
                timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
                text="I was born in Boston in 1990.",
            ),
        ),
        persona_id="01J0000000000000000000ABCD",
    )


@pytest.mark.asyncio
async def test_fanout_returns_results_for_all_extractors() -> None:
    """run() returns a dict keyed by domain for every extractor."""
    bio_gw = MagicMock()
    bio_gw.complete.return_value = json.dumps(
        {"birth_date": "1990-01-01", "birth_date_precision": "year"}
    )
    exp_gw = MagicMock()
    exp_gw.complete.return_value = json.dumps({"parent_event_id": None, "children": []})

    fanout = ExtractionFanout(
        extractors=[
            BiographyExtractor(gateway=bio_gw),
            ExperiencesExtractor(gateway=exp_gw),
        ]
    )
    results = await fanout.run(_chunk())

    assert set(results.keys()) == {"biography", "experiences"}
    assert isinstance(results["biography"], list)
    assert isinstance(results["experiences"], list)
    assert len(results["biography"]) == 1
    assert len(results["experiences"]) == 1


@pytest.mark.asyncio
async def test_fanout_each_extractor_called_once() -> None:
    """Each underlying extractor's gateway is called exactly once."""
    bio_gw = MagicMock()
    bio_gw.complete.return_value = json.dumps({})
    exp_gw = MagicMock()
    exp_gw.complete.return_value = json.dumps({"parent_event_id": None, "children": []})

    fanout = ExtractionFanout(
        extractors=[
            BiographyExtractor(gateway=bio_gw),
            ExperiencesExtractor(gateway=exp_gw),
        ]
    )
    await fanout.run(_chunk())

    bio_gw.complete.assert_called_once()
    exp_gw.complete.assert_called_once()
