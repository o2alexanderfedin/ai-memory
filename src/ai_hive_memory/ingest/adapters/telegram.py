"""TelegramAdapter — parse a Telegram JSON export into canonical Messages."""
from __future__ import annotations

import json
from datetime import datetime

from ai_hive_memory.ingest.messages import Message


class TelegramAdapter:
    """Parse a Telegram ``result.json`` export into canonical Messages."""

    fmt: str = "telegram"

    def parse(self, raw: bytes) -> list[Message]:
        parsed: object = json.loads(raw.decode("utf-8"))
        messages_field: list[object] = (
            parsed.get("messages", [])
            if isinstance(parsed, dict)
            else []
        )
        out: list[Message] = []
        for entry in messages_field:
            if not isinstance(entry, dict):
                continue
            speaker = entry.get("from")
            ts_str = entry.get("date")
            text = entry.get("text")
            if (
                not isinstance(speaker, str)
                or not isinstance(ts_str, str)
                or not isinstance(text, str)
                or not text
            ):
                continue
            out.append(
                Message(
                    speaker=speaker,
                    timestamp=datetime.fromisoformat(ts_str),
                    text=text,
                )
            )
        return out
