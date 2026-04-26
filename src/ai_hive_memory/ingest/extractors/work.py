"""Work domain extractor (US-2.6)."""
from pydantic import BaseModel

from ai_hive_memory.ingest.extractors.base import BaseExtractor
from ai_hive_memory.schemas.work import Work, WorkFields


class WorkExtractor(BaseExtractor):
    """Extracts work/career facts from a chunk."""

    @property
    def domain(self) -> str:
        return "work"

    @property
    def schema_version(self) -> str:
        return "1.0"

    @property
    def fields_model(self) -> type[BaseModel]:
        return WorkFields

    @property
    def fact_model(self) -> type[BaseModel]:
        return Work

    @property
    def system_prompt(self) -> str:
        return (
            "Extract work and career facts from the conversation. "
            "Return a JSON object. "
            "Do NOT include any fields outside this schema."
        )
