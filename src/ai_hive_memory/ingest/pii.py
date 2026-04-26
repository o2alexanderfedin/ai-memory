"""LitePIIScrubber — regex-based SSN and credit-card redaction (Decision 12).

Presidio integration is deferred; this covers the most common PII patterns
without adding a heavy ML dependency.
"""
import re
from collections.abc import Iterator
from dataclasses import dataclass

from ai_hive_memory.ingest.messages import Message

# Social Security Number: ddd-dd-dddd or ddd dd dddd
_SSN_RE = re.compile(r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b")

# Credit card: 12-19 digits, optionally separated by spaces or dashes
_CC_RE = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")


@dataclass
class LitePIIScrubber:
    """Redacts SSN and credit-card patterns from message text."""

    def scrub(self, msg: Message) -> Message:
        """Return a new Message with PII replaced by redaction tokens."""
        text = _SSN_RE.sub("[REDACTED-SSN]", msg.text)
        text = _CC_RE.sub("[REDACTED-CC]", text)
        if text == msg.text:
            return msg
        return msg.model_copy(update={"text": text})

    def scrub_batch(self, msgs: list[Message]) -> Iterator[Message]:
        """Yield scrubbed versions of every message in the list."""
        for msg in msgs:
            yield self.scrub(msg)
