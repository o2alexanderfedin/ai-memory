"""Shared types reused across domain schemas (DIR-1.6, DIR-1.8)."""
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DatePrecision(StrEnum):
    """ISO-8601 date precision marker (DIR-1.8)."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class DomainRef(BaseModel):  # type: ignore[explicit-any]
    """Cross-domain reference dual-field shape (DIR-1.6)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    raw: str = Field(alias="_raw")
    ref: str | None = Field(default=None, alias="_ref")
