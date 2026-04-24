"""Biography domain schema (DIR-1.1, DIR-1.6, DIR-1.8)."""
from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ai_hive_memory.schemas.envelope import CommonEnvelope
from ai_hive_memory.schemas.types import DatePrecision, DomainRef

__all__ = ["Biography", "BiographyFields", "DatePrecision", "DomainRef", "EducationRecord"]


class EducationRecord(BaseModel):  # type: ignore[explicit-any]
    model_config = ConfigDict(extra="forbid")

    degree: str
    field: str
    institution: DomainRef
    year: Annotated[int, Field(ge=1900, le=2100)]


class BiographyFields(BaseModel):  # type: ignore[explicit-any]
    """Typed sub-fields for Biography (DIR-1.8)."""

    model_config = ConfigDict(extra="forbid")

    place_of_birth: DomainRef | None = None
    birth_date: date | None = None
    birth_date_precision: DatePrecision | None = None
    education: list[EducationRecord] = Field(default_factory=list)


class Biography(BaseModel):  # type: ignore[explicit-any]
    """One Biography fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: BiographyFields
