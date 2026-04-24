"""Work domain schema (DIR-1.1, DIR-1.3)."""
from pydantic import BaseModel, ConfigDict

from ai_hive_memory.schemas.envelope import CommonEnvelope


class WorkFields(BaseModel):  # type: ignore[explicit-any]
    """Typed sub-fields for Work (MVP-minimal; full fields in Epic 2)."""

    model_config = ConfigDict(extra="forbid")


class Work(BaseModel):  # type: ignore[explicit-any]
    """One Work fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: WorkFields
