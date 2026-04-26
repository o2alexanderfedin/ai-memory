"""WhatsAppAdapter — parse `[YYYY-MM-DD HH:MM] Speaker: text` lines."""
from datetime import datetime

from ai_hive_memory.ingest.adapters.whatsapp import WhatsAppAdapter


def test_parse_two_line_export() -> None:
    raw = (
        b"[2026-04-21 12:00] Alice: Hi Bob!\n"
        b"[2026-04-21 12:01] Bob: Hey Alice, how are you?\n"
    )
    msgs = WhatsAppAdapter().parse(raw)
    assert len(msgs) == 2  # noqa: PLR2004
    assert msgs[0].speaker == "Alice"
    assert msgs[0].text == "Hi Bob!"
    assert msgs[0].timestamp == datetime.fromisoformat("2026-04-21T12:00:00")
    assert msgs[1].speaker == "Bob"


def test_parse_continuation_lines_attach_to_prior_message() -> None:
    raw = (
        b"[2026-04-21 12:00] Alice: Line 1\n"
        b"still part of Alice's message\n"
        b"[2026-04-21 12:01] Bob: ok\n"
    )
    msgs = WhatsAppAdapter().parse(raw)
    assert len(msgs) == 2  # noqa: PLR2004
    assert msgs[0].text == "Line 1\nstill part of Alice's message"


def test_fmt_attribute_is_whatsapp() -> None:
    assert WhatsAppAdapter().fmt == "whatsapp"
