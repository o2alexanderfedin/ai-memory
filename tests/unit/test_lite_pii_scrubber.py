"""LitePIIScrubber — regex-based SSN and credit-card redaction."""
from datetime import UTC, datetime

from ai_hive_memory.ingest.messages import Message
from ai_hive_memory.ingest.pii import LitePIIScrubber


def _msg(text: str) -> Message:
    return Message(
        speaker="Alice",
        timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
        text=text,
    )


def test_clean_message_is_unchanged() -> None:
    scrubber = LitePIIScrubber()
    msg = _msg("Hello, how are you?")
    result = scrubber.scrub(msg)
    assert result.text == "Hello, how are you?"


def test_ssn_with_dashes_is_redacted() -> None:
    scrubber = LitePIIScrubber()
    msg = _msg("My SSN is 123-45-6789.")
    result = scrubber.scrub(msg)
    assert "123-45-6789" not in result.text
    assert "[REDACTED-SSN]" in result.text


def test_ssn_with_spaces_is_redacted() -> None:
    scrubber = LitePIIScrubber()
    msg = _msg("SSN: 123 45 6789")
    result = scrubber.scrub(msg)
    assert "123 45 6789" not in result.text
    assert "[REDACTED-SSN]" in result.text


def test_credit_card_is_redacted() -> None:
    scrubber = LitePIIScrubber()
    msg = _msg("Card number: 4111111111111111")
    result = scrubber.scrub(msg)
    assert "4111111111111111" not in result.text
    assert "[REDACTED-CC]" in result.text


def test_scrub_batch_applies_to_all_messages() -> None:
    scrubber = LitePIIScrubber()
    msgs = [_msg("SSN 123-45-6789"), _msg("Card 4111-1111-1111-1111")]
    results = list(scrubber.scrub_batch(msgs))
    assert "[REDACTED-SSN]" in results[0].text
    assert "[REDACTED-CC]" in results[1].text
