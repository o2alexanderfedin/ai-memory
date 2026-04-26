"""WhatsAppAdapter — parse ``[YYYY-MM-DD HH:MM] Speaker: text`` exports."""
from __future__ import annotations

import re
from datetime import datetime

from ai_hive_memory.ingest.messages import Message

# Matches lines that start a new message, e.g. "[2026-04-21 12:00] Alice: Hi!"
_HEADER_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] ([^:]+): (.*)$"
)


class WhatsAppAdapter:
    """Parse a WhatsApp plaintext export into canonical Messages."""

    fmt: str = "whatsapp"

    def parse(self, raw: bytes) -> list[Message]:
        lines = raw.decode("utf-8").splitlines()

        # Accumulate (timestamp, speaker, [text_lines]) tuples
        segments: list[tuple[datetime, str, list[str]]] = []

        for line in lines:
            m = _HEADER_RE.match(line)
            if m:
                ts = datetime.fromisoformat(m.group(1).replace(" ", "T"))
                segments.append((ts, m.group(2), [m.group(3)]))
            elif segments:
                # Continuation line — append to the last segment's text
                segments[-1][2].append(line)

        return [
            Message(
                speaker=speaker,
                timestamp=ts,
                text="\n".join(text_lines),
            )
            for ts, speaker, text_lines in segments
        ]
