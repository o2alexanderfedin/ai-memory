"""Psychometrics domain extractor (US-2.6)."""
from pydantic import BaseModel

from ai_hive_memory.ingest.extractors.base import BaseExtractor
from ai_hive_memory.schemas.psychometrics import Psychometrics, PsychometricsFields


class PsychometricsExtractor(BaseExtractor):
    """Extracts psychometric/personality facts from a chunk."""

    @property
    def domain(self) -> str:
        return "psychometrics"

    @property
    def schema_version(self) -> str:
        return "1.0"

    @property
    def fields_model(self) -> type[BaseModel]:
        return PsychometricsFields

    @property
    def fact_model(self) -> type[BaseModel]:
        return Psychometrics

    @property
    def system_prompt(self) -> str:
        return (
            "Extract psychometric and personality facts from the conversation. "
            "Return a JSON object. "
            "Do NOT include any fields outside this schema."
        )
