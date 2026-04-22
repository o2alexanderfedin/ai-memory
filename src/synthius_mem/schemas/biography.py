"""Biography domain schema (DIR-1.1, DIR-1.6, DIR-1.8)."""
from datetime import date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from synthius_mem.schemas.envelope import CommonEnvelope


class DatePrecision(str, Enum):
    """ISO-8601 date precision marker (DIR-1.8)."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class DomainRef(BaseModel):  # type: ignore[explicit-any]
    """Cross-domain reference dual-field shape (DIR-1.6)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    raw: str = Field(alias="_raw")
    ref: str | None = Field(default=None, alias="_ref")


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
