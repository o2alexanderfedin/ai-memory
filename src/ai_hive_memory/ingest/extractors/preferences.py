"""Preferences domain extractor (US-2.6)."""
from pydantic import BaseModel

from ai_hive_memory.ingest.extractors.base import BaseExtractor
from ai_hive_memory.schemas.preferences import Preferences, PreferencesFields


class PreferencesExtractor(BaseExtractor):
    """Extracts preference facts from a chunk."""

    @property
    def domain(self) -> str:
        return "preferences"

    @property
    def schema_version(self) -> str:
        return "1.0"

    @property
    def fields_model(self) -> type[BaseModel]:
        return PreferencesFields

    @property
    def fact_model(self) -> type[BaseModel]:
        return Preferences

    @property
    def system_prompt(self) -> str:
        return (
            "Extract preference facts from the conversation. "
            "Return a JSON object. "
            "Do NOT include any fields outside this schema."
        )
