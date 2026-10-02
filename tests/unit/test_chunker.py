"""Chunker — token-aware sliding window with whole-message overlap."""
from datetime import UTC, datetime

import pytest

from ai_hive_memory.ingest.chunker import Chunk, Chunker
from ai_hive_memory.ingest.messages import Message


def _msg(speaker: str, text: str) -> Message:
    return Message(
        speaker=speaker,
        timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
        text=text,
    )


def test_small_batch_fits_in_one_chunk() -> None:
    chunker = Chunker()
    msgs = [_msg("Alice", "hi"), _msg("Bob", "hello")]
    chunks = list(chunker.chunk(msgs))
    assert len(chunks) == 1
    assert len(chunks[0].messages) == 2  # noqa: PLR2004


def test_chunk_carries_persona_id() -> None:
    chunker = Chunker()
    msgs = [_msg("Alice", "hi")]
    chunks = list(chunker.chunk(msgs, persona_id="p-123"))
    assert chunks[0].persona_id == "p-123"


def test_large_batch_splits_into_multiple_chunks() -> None:
    """Feed enough messages to force at least two chunks.

    Each message with 'word '*5 is ~26 tokens (header + text).
    window_tokens=60 fits at most 2 messages (52 tok), so 6 messages => >= 3 chunks.
    """
    chunker = Chunker(window_tokens=60, overlap_tokens=26)
    msgs = [_msg("Alice", "word " * 5) for _ in range(6)]
    chunks = list(chunker.chunk(msgs))
    assert len(chunks) >= 2  # noqa: PLR2004


def test_overlap_repeats_messages_across_chunk_boundary() -> None:
    """Last message(s) of chunk N appear at the start of chunk N+1.

    window_tokens=60 fits 2 messages (~26 tok each).
    overlap_tokens=26 keeps the last message for the next chunk.
    """
    chunker = Chunker(window_tokens=60, overlap_tokens=26)
    msgs = [_msg("Alice", "word " * 5) for _ in range(6)]
    chunks = list(chunker.chunk(msgs))
    # At least one message is shared between consecutive chunks
    set_a = {id(m) for m in chunks[0].messages}
    set_b = {id(m) for m in chunks[1].messages}
    assert set_a & set_b, "Expected overlap between consecutive chunks"


@pytest.mark.parametrize("persona_id", [None, "p-abc"])
def test_chunk_is_frozen_dataclass(persona_id: str | None) -> None:
    chunker = Chunker()
    msgs = [_msg("Alice", "hi")]
    chunk = next(iter(chunker.chunk(msgs, persona_id=persona_id)))
    assert isinstance(chunk, Chunk)
    with pytest.raises((AttributeError, TypeError)):
        chunk.persona_id = "mutated"  # type: ignore[misc]


def test_carried_overlap_never_pushes_a_chunk_past_the_window() -> None:
    """Overlap plus the next message must still fit in window_tokens.

    With header overhead, 'word '*10 is 31 tokens, 'word '*3 is 24 and
    'word '*30 is 51.  The first chunk is [31, 24] = 55.  The 24-token message
    fits the 26-token overlap budget, but 24 + 51 = 75 exceeds the 60-token
    window, so the overlap must be dropped rather than carried.
    """
    chunker = Chunker(window_tokens=60, overlap_tokens=26)
    msgs = [_msg("Alice", "word " * 10), _msg("Bob", "word " * 3),
            _msg("Alice", "word " * 30)]
    assert [chunker._tokens(m) for m in msgs] == [31, 24, 51]

    chunks = list(chunker.chunk(msgs))

    sizes = [sum(chunker._tokens(m) for m in c.messages) for c in chunks]
    assert all(s <= chunker.window_tokens for s in sizes), sizes
    # No message is lost while the overlap is dropped.
    assert {id(m) for c in chunks for m in c.messages} == {id(m) for m in msgs}
