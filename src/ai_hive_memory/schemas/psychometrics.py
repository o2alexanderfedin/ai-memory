"""Psychometrics domain schema (DIR-1.1, DIR-1.3)."""
from pydantic import BaseModel, ConfigDict

from ai_hive_memory.schemas.envelope import CommonEnvelope


class PsychometricsFields(BaseModel):  # type: ignore[explicit-any]
    """Typed sub-fields for Psychometrics (MVP-minimal; full fields in Epic 2)."""

    model_config = ConfigDict(extra="forbid")


class Psychometrics(BaseModel):  # type: ignore[explicit-any]
    """One Psychometrics fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: PsychometricsFields
