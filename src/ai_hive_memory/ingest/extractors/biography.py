"""Biography domain extractor (US-2.6)."""
from pydantic import BaseModel

from ai_hive_memory.ingest.extractors.base import BaseExtractor
from ai_hive_memory.schemas.biography import Biography, BiographyFields


class BiographyExtractor(BaseExtractor):
    """Extracts biographical facts (birth date, place, education) from a chunk."""

    @property
    def domain(self) -> str:
        return "biography"

    @property
    def schema_version(self) -> str:
        return "1.0"

    @property
    def fields_model(self) -> type[BaseModel]:
        return BiographyFields

    @property
    def fact_model(self) -> type[BaseModel]:
        return Biography

    @property
    def system_prompt(self) -> str:
        return (
            "Extract biographical facts from the conversation. "
            "Return a JSON object with fields: "
            "place_of_birth (object with _raw and optional _ref), "
            "birth_date (ISO date string or null), "
            "birth_date_precision (year|month|day or null), "
            "education (list of {degree, field, institution, year} or []). "
            "Only include fields where information is present. "
            "Do NOT include any fields outside this schema."
        )
