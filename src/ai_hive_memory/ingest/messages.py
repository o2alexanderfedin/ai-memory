"""Canonical Message — output of every IngestAdapter, input to the rest of the pipeline."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):  # type: ignore[explicit-any]
    """One canonical message in a conversation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    speaker: str
    timestamp: datetime
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)
    # Which occurrence of the same (speaker, timestamp, text) in one upload
    # this is: 1 for the first, 2 for the second, and so on. WhatsApp shows
    # minutes only, so one person can send the same text twice in a minute.
    repeat: int = Field(default=1, ge=1)

    def canonical_signature(self) -> str:
        """Deterministic string used for SHA-256 idempotency (DIR-3.1).

        Excludes metadata: re-uploading the same conversation with different
        metadata still dedupes. A repeat adds its number, so it is kept as a
        message of its own; the first occurrence's signature is unchanged.
        """
        signature = f"{self.speaker}|{self.timestamp.isoformat()}|{self.text}"
        return signature if self.repeat == 1 else f"{signature}|{self.repeat}"
