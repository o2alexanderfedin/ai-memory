"""SpeakerHeader — renders a Chunk into a headed transcript string (US-2.5 DIR-3.3)."""
from dataclasses import dataclass

from ai_hive_memory.ingest.chunker import Chunk


@dataclass
class SpeakerHeader:
    """Formats a Chunk as a plain-text transcript with a speaker roster header.

    Output format::

        Speakers: Alice, Bob
        [Alice:2026-04-21T12:00:00+00:00] hi
        [Bob:2026-04-21T12:00:00+00:00] yo
    """

    def render(self, chunk: Chunk) -> str:
        """Return the headed transcript string for *chunk*."""
        # Deduplicated, insertion-order speaker roster
        seen: set[str] = set()
        roster: list[str] = []
        for msg in chunk.messages:
            if msg.speaker not in seen:
                seen.add(msg.speaker)
                roster.append(msg.speaker)

        header_line = "Speakers: " + ", ".join(roster)

        inline_lines = [
            f"[{msg.speaker}:{msg.timestamp.isoformat()}] {msg.text}"
            for msg in chunk.messages
        ]

        return "\n".join([header_line, *inline_lines])
