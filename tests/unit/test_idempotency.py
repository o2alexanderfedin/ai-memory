"""IdempotencyGuard — SHA-256 of canonical signature; filters seen messages."""
from datetime import UTC, datetime

from ai_hive_memory.ingest.idempotency import IdempotencyGuard
from ai_hive_memory.ingest.messages import Message


def _msg(speaker: str, text: str) -> Message:
    return Message(
        speaker=speaker,
        timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
        text=text,
    )


def test_hash_for_message_is_64_char_hex() -> None:
    guard = IdempotencyGuard(seen_hashes=set())
    h = guard.hash_for(_msg("Alice", "hi"))
    assert len(h) == 64  # noqa: PLR2004
    assert all(c in "0123456789abcdef" for c in h)


def test_filter_passes_unseen_messages_through() -> None:
    guard = IdempotencyGuard(seen_hashes=set())
    msgs = [_msg("Alice", "hi"), _msg("Bob", "hello")]
    result = list(guard.filter_unseen(msgs))
    assert len(result) == 2  # noqa: PLR2004


def test_filter_drops_messages_whose_hashes_are_in_seen() -> None:
    msgs = [_msg("Alice", "hi"), _msg("Bob", "hello")]
    seen = {IdempotencyGuard(seen_hashes=set()).hash_for(msgs[0])}
    guard = IdempotencyGuard(seen_hashes=seen)
    result = list(guard.filter_unseen(msgs))
    assert len(result) == 1
    assert result[0].speaker == "Bob"


def test_filter_drops_duplicates_within_same_batch() -> None:
    """Two identical messages in one upload — only the first survives."""
    guard = IdempotencyGuard(seen_hashes=set())
    msgs = [_msg("Alice", "hi"), _msg("Alice", "hi")]
    result = list(guard.filter_unseen(msgs))
    assert len(result) == 1
