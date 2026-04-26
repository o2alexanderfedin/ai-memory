"""SocialCircle domain extractor (US-2.6)."""
from pydantic import BaseModel

from ai_hive_memory.ingest.extractors.base import BaseExtractor
from ai_hive_memory.schemas.social_circle import SocialCircle, SocialCircleFields


class SocialCircleExtractor(BaseExtractor):
    """Extracts social relationship facts from a chunk."""

    @property
    def domain(self) -> str:
        return "social_circle"

    @property
    def schema_version(self) -> str:
        return "1.0"

    @property
    def fields_model(self) -> type[BaseModel]:
        return SocialCircleFields

    @property
    def fact_model(self) -> type[BaseModel]:
        return SocialCircle

    @property
    def system_prompt(self) -> str:
        return (
            "Extract social relationship facts from the conversation. "
            "Return a JSON object with fields: "
            "relations (list of {person: {_raw, _ref}, kind, closeness} or []). "
            "Do NOT include any fields outside this schema."
        )
