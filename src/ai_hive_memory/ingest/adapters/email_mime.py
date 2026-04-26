"""EmailMIMEAdapter — parse raw MIME email bytes into canonical Messages."""
from __future__ import annotations

import email
import email.message
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from ai_hive_memory.ingest.messages import Message


class EmailMIMEAdapter:
    """Parse a raw MIME email (bytes) into a single canonical Message."""

    fmt: str = "email"

    def parse(self, raw: bytes) -> list[Message]:
        msg = email.message_from_bytes(raw)

        sender = str(msg.get("From", "unknown"))
        subject = str(msg.get("Subject", ""))

        # Parse the Date header, fall back to now(UTC)
        date_header = msg.get("Date")
        if date_header:
            try:
                ts = parsedate_to_datetime(str(date_header))
                # Ensure timezone-aware; if naive treat as UTC
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=UTC)
            except Exception:
                ts = datetime.now(UTC)
        else:
            ts = datetime.now(UTC)

        body = _extract_text(msg)

        metadata: dict[str, str] = {}
        if subject:
            metadata["subject"] = subject

        return [
            Message(
                speaker=sender,
                timestamp=ts,
                text=body,
                metadata=metadata,
            )
        ]


def _extract_text(msg: email.message.Message) -> str:
    """Return the plain-text body, collapsing multipart if needed."""
    if msg.is_multipart():
        parts: list[str] = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = part.get_content_charset() or "utf-8"
                    parts.append(payload.decode(charset, errors="replace"))
        return "\n".join(parts).strip()

    payload = msg.get_payload(decode=True)
    if isinstance(payload, bytes):
        charset = msg.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace").strip()
    return str(payload or "").strip()
