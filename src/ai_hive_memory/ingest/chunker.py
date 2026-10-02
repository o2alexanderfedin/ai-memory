"""Chunker — token-aware sliding-window chunking with whole-message overlap (US-2.5)."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

import tiktoken

from ai_hive_memory.ingest.messages import Message


@dataclass(frozen=True)
class Chunk:
    """An ordered slice of messages that fits within the token window."""

    messages: tuple[Message, ...]
    persona_id: str | None = None
    extras: dict[str, str] = field(default_factory=dict)


@dataclass
class Chunker:
    """Splits a message list into overlapping token-bounded chunks.

    Each chunk stays within *window_tokens*.  The last *overlap_tokens* worth
    of whole messages from one chunk are repeated at the start of the next so
    downstream embedding has continuity context; overlap is dropped, oldest
    first, when it would push the next chunk past the window.  A single
    message larger than the window is emitted alone, because messages are
    never split (US-2.5).

    Token counting includes the [Speaker:Timestamp] overhead that
    SpeakerHeader will later add — avoids silent truncation at embed time.
    """

    window_tokens: int = 2000
    overlap_tokens: int = 200
    encoding_name: str = "cl100k_base"

    def __post_init__(self) -> None:
        self._enc = tiktoken.get_encoding(self.encoding_name)

    def _tokens(self, msg: Message) -> int:
        """Count tokens for a message including its SpeakerHeader prefix."""
        header = f"[{msg.speaker}:{msg.timestamp.isoformat()}] "
        return len(self._enc.encode(header + msg.text))

    def chunk(
        self,
        msgs: list[Message],
        persona_id: str | None = None,
    ) -> Iterator[Chunk]:
        """Yield Chunks; whole-message overlap at each window boundary."""
        if not msgs:
            return

        window: list[Message] = []
        window_tok = 0

        for msg in msgs:
            msg_tok = self._tokens(msg)

            # If this single message exceeds the window, emit it alone.
            if msg_tok >= self.window_tokens:
                if window:
                    yield Chunk(messages=tuple(window), persona_id=persona_id)
                yield Chunk(messages=(msg,), persona_id=persona_id)
                window = []
                window_tok = 0
                continue

            if window_tok + msg_tok > self.window_tokens:
                # Emit the current window.
                yield Chunk(messages=tuple(window), persona_id=persona_id)

                # Build overlap: walk backwards until overlap budget exhausted.
                overlap: list[Message] = []
                overlap_tok = 0
                for prev in reversed(window):
                    t = self._tokens(prev)
                    if overlap_tok + t > self.overlap_tokens:
                        break
                    overlap.insert(0, prev)
                    overlap_tok += t

                # Drop the oldest overlap messages until the incoming message
                # fits; otherwise this chunk would exceed window_tokens.
                while overlap and overlap_tok + msg_tok > self.window_tokens:
                    overlap_tok -= self._tokens(overlap.pop(0))

                window = overlap
                window_tok = overlap_tok

            window.append(msg)
            window_tok += msg_tok

        if window:
            yield Chunk(messages=tuple(window), persona_id=persona_id)
