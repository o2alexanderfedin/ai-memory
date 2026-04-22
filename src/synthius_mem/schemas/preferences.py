"""Preferences domain schema (DIR-1.1, DIR-1.3)."""
from pydantic import BaseModel, ConfigDict

from synthius_mem.schemas.envelope import CommonEnvelope


class PreferencesFields(BaseModel):  # type: ignore[explicit-any]
    """Typed sub-fields for Preferences (MVP-minimal; full fields in Epic 2)."""

    model_config = ConfigDict(extra="forbid")


class Preferences(BaseModel):  # type: ignore[explicit-any]
    """One Preferences fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: PreferencesFields
