"""Format-specific adapters: bytes-in, canonical Message[]-out (DIR-3.1)."""
from typing import Protocol, runtime_checkable

from ai_hive_memory.ingest.messages import Message


class UnknownFormatError(Exception):
    """Raised when an unregistered format name is requested."""


@runtime_checkable
class IngestAdapter(Protocol):
    """Contract for every format adapter."""

    fmt: str

    def parse(self, raw: bytes) -> list[Message]:
        """Normalize raw upload bytes to canonical Message[]."""
        ...


class AdapterRouter:
    """Dispatches a raw upload to the correct IngestAdapter by format name."""

    def __init__(self) -> None:
        self._adapters: dict[str, IngestAdapter] = {}

    def register(self, fmt: str, adapter: IngestAdapter) -> None:
        self._adapters[fmt] = adapter

    def parse(self, fmt: str, raw: bytes) -> list[Message]:
        if fmt not in self._adapters:
            raise UnknownFormatError(f"unknown format: {fmt}")
        return self._adapters[fmt].parse(raw)

    def supported_formats(self) -> list[str]:
        return list(self._adapters.keys())
