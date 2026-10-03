"""IdempotencyGuard — SHA-256 of canonical signature; filters seen messages."""
import hashlib
from datetime import UTC, datetime

from ai_hive_memory.ingest.idempotency import IdempotencyGuard, number_repeats
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


def test_repeats_in_one_upload_get_their_own_hash() -> None:
    """The same text twice in one minute is two messages, not one."""
    msgs = number_repeats([_msg("Alice", "hi"), _msg("Bob", "hi"),
                           _msg("Alice", "hi"), _msg("Alice", "hi")])
    assert [m.repeat for m in msgs] == [1, 1, 2, 3]
    guard = IdempotencyGuard(seen_hashes=set())
    assert len(set(map(guard.hash_for, msgs))) == 4  # noqa: PLR2004
    assert len(list(guard.filter_unseen(msgs))) == 4  # noqa: PLR2004


def test_first_occurrence_keeps_the_hash_stored_before_repeats_were_numbered() -> None:
    """Messages ingested earlier must still be recognised on re-upload (US-2.3)."""
    (first, _) = number_repeats([_msg("Alice", "hi"), _msg("Alice", "hi")])
    old_hash = hashlib.sha256(b"Alice|2026-04-21T12:00:00+00:00|hi").hexdigest()
    assert IdempotencyGuard().hash_for(first) == old_hash
