"""SpeakerHeader inliner — formats a Chunk into a headed transcript string."""
from datetime import UTC, datetime

from ai_hive_memory.ingest.chunker import Chunk
from ai_hive_memory.ingest.messages import Message
from ai_hive_memory.ingest.speaker_header import SpeakerHeader


def _msg(speaker: str, text: str) -> Message:
    return Message(
        speaker=speaker,
        timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
        text=text,
    )


def test_render_includes_speaker_roster() -> None:
    chunk = Chunk(messages=(_msg("Alice", "hi"), _msg("Bob", "yo")))
    header = SpeakerHeader()
    result = header.render(chunk)
    assert result.startswith("Speakers: ")
    assert "Alice" in result
    assert "Bob" in result


def test_render_inline_format() -> None:
    """Each message is formatted as [Speaker:ISO-timestamp] text."""
    chunk = Chunk(messages=(_msg("Alice", "hi"), _msg("Bob", "yo")))
    header = SpeakerHeader()
    result = header.render(chunk)
    assert "[Alice:2026-04-21T12:00:00+00:00] hi" in result
    assert "[Bob:2026-04-21T12:00:00+00:00] yo" in result


def test_render_full_output_structure() -> None:
    """Roster line, blank line, then inline messages."""
    chunk = Chunk(messages=(_msg("Alice", "hi"), _msg("Bob", "yo")))
    header = SpeakerHeader()
    result = header.render(chunk)
    lines = result.splitlines()
    assert lines[0].startswith("Speakers:")
    # Inline message lines present somewhere after the roster
    inline_lines = [ln for ln in lines if ln.startswith("[")]
    assert len(inline_lines) == 2  # noqa: PLR2004
