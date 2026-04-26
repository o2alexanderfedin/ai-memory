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

    def canonical_signature(self) -> str:
        """Deterministic string used for SHA-256 idempotency (DIR-3.1).

        Excludes metadata: re-uploading the same conversation with different
        metadata still dedupes.
        """
        return f"{self.speaker}|{self.timestamp.isoformat()}|{self.text}"
