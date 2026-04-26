"""TelegramAdapter — parse JSON export shape."""
import json

from ai_hive_memory.ingest.adapters.telegram import TelegramAdapter


def test_parse_two_messages_from_json_export() -> None:
    payload = {
        "messages": [
            {"from": "Alice", "date": "2026-04-21T12:00:00", "text": "Hi Bob!"},
            {"from": "Bob", "date": "2026-04-21T12:01:00", "text": "Hey!"},
        ]
    }
    raw = json.dumps(payload).encode()
    msgs = TelegramAdapter().parse(raw)
    assert len(msgs) == 2  # noqa: PLR2004
    assert msgs[0].speaker == "Alice"
    assert msgs[0].text == "Hi Bob!"
    assert msgs[1].speaker == "Bob"


def test_parse_skips_service_messages_without_text() -> None:
    payload = {
        "messages": [
            {"from": "Alice", "date": "2026-04-21T12:00:00", "text": "hi"},
            {"type": "service", "action": "join_by_link"},
            {"from": "Bob", "date": "2026-04-21T12:01:00", "text": "yo"},
        ]
    }
    msgs = TelegramAdapter().parse(json.dumps(payload).encode())
    assert len(msgs) == 2  # noqa: PLR2004


def test_fmt_attribute_is_telegram() -> None:
    assert TelegramAdapter().fmt == "telegram"
