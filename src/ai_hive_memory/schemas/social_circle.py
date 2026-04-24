"""SocialCircle domain schema (DIR-1.1, DIR-1.3, DIR-1.6)."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ai_hive_memory.schemas.envelope import CommonEnvelope
from ai_hive_memory.schemas.types import DomainRef


class SocialRelation(BaseModel):  # type: ignore[explicit-any]
    """A single person relationship entry with DomainRef cross-domain link (DIR-1.6)."""

    model_config = ConfigDict(extra="forbid")

    person: DomainRef
    kind: str
    closeness: Annotated[float, Field(ge=0.0, le=1.0)]


class SocialCircleFields(BaseModel):  # type: ignore[explicit-any]
    """Typed sub-fields for SocialCircle."""

    model_config = ConfigDict(extra="forbid")

    relations: list[SocialRelation] = Field(default_factory=list)


class SocialCircle(BaseModel):  # type: ignore[explicit-any]
    """One SocialCircle fact = envelope + typed fields."""

    model_config = ConfigDict(extra="forbid")

    envelope: CommonEnvelope
    fields: SocialCircleFields
