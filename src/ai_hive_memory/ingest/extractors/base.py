"""BaseExtractor: abstract LLM extraction with closed-schema validation (US-2.6)."""
from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from ai_hive_memory.ingest.chunker import Chunk
from ai_hive_memory.llm.gateway import LLMGateway
from ai_hive_memory.llm.models import ModelTier
from ai_hive_memory.schemas.envelope import CommonEnvelope, Provenance

_EXTRACTOR_VERSION = "1.0.0"


@dataclass
class BaseExtractor(ABC):
    """Abstract per-domain extractor.

    Subclasses declare:
      - domain: str          — e.g. "biography"
      - schema_version: str  — e.g. "1.0"
      - fields_model         — Pydantic model for the fields block (extra="forbid")
      - fact_model           — Pydantic model for the full fact (envelope + fields)
      - system_prompt: str   — task instruction for the LLM

    The extract() method drives: format chunk → LLM → validate fields → assemble fact.
    """

    gateway: LLMGateway

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain name string, e.g. 'biography'."""

    @property
    @abstractmethod
    def schema_version(self) -> str:
        """Schema version string, e.g. '1.0'."""

    @property
    @abstractmethod
    def fields_model(self) -> type[BaseModel]:
        """Pydantic model for the fields block (must have extra='forbid')."""

    @property
    @abstractmethod
    def fact_model(self) -> type[BaseModel]:
        """Pydantic model for the complete fact (envelope + fields)."""

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt describing the extraction task."""

    def _format_chunk(self, chunk: Chunk) -> str:
        """Render chunk messages into a single string for the LLM prompt."""
        lines: list[str] = []
        for msg in chunk.messages:
            lines.append(f"[{msg.speaker}:{msg.timestamp.isoformat()}] {msg.text}")
        return "\n".join(lines)

    def _build_envelope(self, chunk: Chunk) -> CommonEnvelope:
        """Construct CommonEnvelope with Provenance for this extraction."""
        now = datetime.now(tz=UTC)
        persona_id = chunk.persona_id or ""
        # Use first message id as source reference
        first_msg = chunk.messages[0] if chunk.messages else None
        source_msg_id = (
            first_msg.canonical_signature() if first_msg is not None else "unknown"
        )
        provenance = Provenance(
            source_message_id=source_msg_id,
            source_chunk_id=source_msg_id,
            extracted_at=now,
            extractor_version=_EXTRACTOR_VERSION,
            injection_risk=None,
            pii_tokens_redacted=[],
        )
        return CommonEnvelope(
            persona_id=persona_id,
            domain=self.domain,
            schema_version=self.schema_version,
            confidence=0.8,
            provenance=provenance,
            created_at=now,
            updated_at=now,
        )

    def extract(self, chunk: Chunk) -> list[Any]:  # type: ignore[explicit-any]
        """Extract domain facts from a chunk.

        Returns a list of fact_model instances (typically 0 or 1 element,
        but may be >1 for list-like domains).
        """
        chunk_text = self._format_chunk(chunk)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": chunk_text},
        ]
        raw = self.gateway.complete(
            tier=ModelTier.VOLUME,
            messages=messages,
            json_mode=True,
        )
        data: object = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object from LLM, got {type(data)}")
        fields_data: dict[str, object] = data
        # Validate fields — raises pydantic.ValidationError on extra/invalid fields
        fields = self.fields_model.model_validate(fields_data)
        envelope = self._build_envelope(chunk)
        fact = self.fact_model.model_validate(
            {"envelope": envelope.model_dump(), "fields": fields.model_dump()}
        )
        return [fact]


@dataclass
class ExtractionFanout:
    """Run all 6 domain extractors concurrently over a single chunk (US-2.6)."""

    extractors: list[BaseExtractor]

    async def run(self, chunk: Chunk) -> dict[str, list[BaseModel]]:
        """Extract from all extractors concurrently; return domain → facts mapping."""
        loop = asyncio.get_running_loop()

        async def _run_one(ex: BaseExtractor) -> tuple[str, list[BaseModel]]:
            results = await loop.run_in_executor(None, ex.extract, chunk)
            return ex.domain, results

        pairs: list[tuple[str, list[BaseModel]]] = await asyncio.gather(
            *[_run_one(ex) for ex in self.extractors]
        )
        return dict(pairs)
