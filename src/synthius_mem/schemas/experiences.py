"""Experiences domain schema (DIR-1.1, DIR-1.2, DIR-1.3)."""
from pydantic import BaseModel, ConfigDict, Field

from synthius_mem.schemas.envelope import CommonEnvelope


class ExperiencesFields(BaseModel):  # type: ignore[explicit-any]
    """Typed sub-fields for Experiences (DIR-1.2 part-of decomposition)."""

    model_config = ConfigDict(extra="forbid")

    parent_event_id: str | None = None
    children: list[str] = Field(default_factory=list)


class Experiences(BaseModel):  # type: ignore[explicit-any]
    """One Experiences fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: ExperiencesFields
