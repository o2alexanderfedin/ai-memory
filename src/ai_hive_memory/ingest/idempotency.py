"""IdempotencyGuard — SHA-256 deduplication for ingested messages (DIR-3.1)."""
import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field

from ai_hive_memory.ingest.messages import Message


@dataclass
class IdempotencyGuard:
    """Filters out messages already seen, using SHA-256 of their canonical signature."""

    seen_hashes: set[str] = field(default_factory=set)

    def hash_for(self, msg: Message) -> str:
        """Return a 64-character lowercase hex SHA-256 of the message's canonical signature."""
        return hashlib.sha256(msg.canonical_signature().encode()).hexdigest()

    def filter_unseen(self, msgs: list[Message]) -> Iterator[Message]:
        """Yield only messages whose hash has not been seen (including within this batch)."""
        for msg in msgs:
            h = self.hash_for(msg)
            if h not in self.seen_hashes:
                self.seen_hashes.add(h)
                yield msg
