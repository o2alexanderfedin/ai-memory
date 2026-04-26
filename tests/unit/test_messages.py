"""Canonical Message model — speaker, timestamp, text, metadata."""
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ai_hive_memory.ingest.messages import Message


def test_message_validates_minimal_fields() -> None:
    m = Message(
        speaker="Alice",
        timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
        text="hello world",
    )
    assert m.speaker == "Alice"
    assert m.text == "hello world"
    assert m.metadata == {}


def test_message_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Message.model_validate({
            "speaker": "Alice",
            "timestamp": "2026-04-21T12:00:00Z",
            "text": "hi",
            "unknown_field": "nope",
        })


def test_message_metadata_accepts_string_values() -> None:
    m = Message(
        speaker="Bob",
        timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
        text="hi",
        metadata={"thread_id": "t-1"},
    )
    assert m.metadata["thread_id"] == "t-1"


def test_message_canonical_signature_is_deterministic() -> None:
    """Identical (speaker, ts, text) yields identical canonical_signature regardless of metadata."""
    ts = datetime(2026, 4, 21, 12, 0, tzinfo=UTC)
    a = Message(speaker="Alice", timestamp=ts, text="hi", metadata={"k": "v"})
    b = Message(speaker="Alice", timestamp=ts, text="hi", metadata={})
    assert a.canonical_signature() == b.canonical_signature()
