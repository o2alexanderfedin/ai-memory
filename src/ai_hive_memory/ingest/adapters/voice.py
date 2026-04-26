"""VoiceAdapter — parse pre-transcribed JSON (STT output) into canonical Messages."""
from __future__ import annotations

import json
from datetime import datetime

from ai_hive_memory.ingest.messages import Message


class VoiceAdapter:
    """Parse a pre-transcribed voice JSON export into canonical Messages.

    Expected shape::

        {
            "segments": [
                {"speaker": "Alice", "start": "2026-04-21T12:00:00Z", "text": "..."},
                ...
            ]
        }

    STT (speech-to-text) transcription is assumed to have already occurred;
    raw audio processing is out of scope (deferred).
    """

    fmt: str = "voice"

    def parse(self, raw: bytes) -> list[Message]:
        parsed: object = json.loads(raw.decode("utf-8"))
        segments: list[object] = (
            parsed.get("segments", [])
            if isinstance(parsed, dict)
            else []
        )
        out: list[Message] = []
        for entry in segments:
            if not isinstance(entry, dict):
                continue
            speaker = entry.get("speaker")
            ts_str = entry.get("start")
            text = entry.get("text")
            if (
                not isinstance(speaker, str)
                or not isinstance(ts_str, str)
                or not isinstance(text, str)
                or not text
            ):
                continue
            # Normalise Z-suffix to +00:00 for fromisoformat (Python < 3.11 compat)
            ts_str = ts_str.replace("Z", "+00:00")
            out.append(
                Message(
                    speaker=speaker,
                    timestamp=datetime.fromisoformat(ts_str),
                    text=text,
                )
            )
        return out
