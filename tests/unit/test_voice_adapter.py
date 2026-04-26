"""VoiceAdapter — parse pre-transcribed JSON (STT output shape)."""
import json

from ai_hive_memory.ingest.adapters.voice import VoiceAdapter


def test_parse_two_segments() -> None:
    payload = {
        "segments": [
            {"speaker": "Alice", "start": "2026-04-21T12:00:00Z", "text": "Hello!"},
            {"speaker": "Bob", "start": "2026-04-21T12:00:05Z", "text": "Hi there!"},
        ]
    }
    msgs = VoiceAdapter().parse(json.dumps(payload).encode())
    assert len(msgs) == 2  # noqa: PLR2004
    assert msgs[0].speaker == "Alice"
    assert msgs[0].text == "Hello!"
    assert msgs[1].speaker == "Bob"


def test_parse_skips_segments_missing_fields() -> None:
    payload = {
        "segments": [
            {"speaker": "Alice", "start": "2026-04-21T12:00:00Z", "text": "hi"},
            {"start": "2026-04-21T12:00:02Z", "text": "no speaker"},
            {"speaker": "Bob", "start": "2026-04-21T12:00:05Z", "text": "ok"},
        ]
    }
    msgs = VoiceAdapter().parse(json.dumps(payload).encode())
    assert len(msgs) == 2  # noqa: PLR2004


def test_fmt_attribute_is_voice() -> None:
    assert VoiceAdapter().fmt == "voice"
