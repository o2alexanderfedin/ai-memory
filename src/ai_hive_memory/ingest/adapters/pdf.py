"""PDFAdapter — extract text from PDF bytes, one Message per page."""
from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO

import pypdf

from ai_hive_memory.ingest.messages import Message


class PDFAdapter:
    """Parse PDF bytes into canonical Messages, one per page."""

    fmt: str = "pdf"

    def __init__(self, speaker_label: str = "Document") -> None:
        self.speaker_label = speaker_label

    def parse(self, raw: bytes) -> list[Message]:
        reader = pypdf.PdfReader(BytesIO(raw))
        now = datetime.now(UTC)
        out: list[Message] = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.strip()
            if not text:
                continue
            out.append(
                Message(
                    speaker=self.speaker_label,
                    timestamp=now,
                    text=text,
                    metadata={"page": str(i + 1)},
                )
            )
        return out
