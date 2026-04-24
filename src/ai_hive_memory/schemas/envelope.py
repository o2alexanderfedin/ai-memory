"""CommonEnvelope shared $defs block (DIR-1.3)."""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Provenance(BaseModel):  # type: ignore[explicit-any]
    """Per-fact provenance (DIR-1.5, DIR-9.6)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_message_id: str
    source_chunk_id: str
    extracted_at: datetime
    extractor_version: str
    injection_risk: Annotated[float | None, Field(ge=0.0, le=1.0, default=None)]
    pii_tokens_redacted: Annotated[list[dict[str, str]], Field(default_factory=list)]


class CommonEnvelope(BaseModel):  # type: ignore[explicit-any]
    """Shared envelope across all 6 domain schemas (DIR-1.3)."""

    model_config = ConfigDict(extra="forbid")

    persona_id: str
    domain: str
    schema_version: str
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: Provenance
    created_at: datetime
    updated_at: datetime
