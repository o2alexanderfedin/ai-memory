"""Experiences domain extractor (US-2.6)."""
from pydantic import BaseModel

from ai_hive_memory.ingest.extractors.base import BaseExtractor
from ai_hive_memory.schemas.experiences import Experiences, ExperiencesFields


class ExperiencesExtractor(BaseExtractor):
    """Extracts experience/event facts from a chunk."""

    @property
    def domain(self) -> str:
        return "experiences"

    @property
    def schema_version(self) -> str:
        return "1.0"

    @property
    def fields_model(self) -> type[BaseModel]:
        return ExperiencesFields

    @property
    def fact_model(self) -> type[BaseModel]:
        return Experiences

    @property
    def system_prompt(self) -> str:
        return (
            "Extract experience/event facts from the conversation. "
            "Return a JSON object with fields: "
            "parent_event_id (string or null), "
            "children (list of event id strings, default []). "
            "Do NOT include any fields outside this schema."
        )
