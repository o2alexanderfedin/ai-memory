"""IngestAdapter Protocol + AdapterRouter — format dispatch."""
from datetime import UTC, datetime

import pytest

from ai_hive_memory.ingest.adapters import (
    AdapterRouter,
    IngestAdapter,
    UnknownFormatError,
)
from ai_hive_memory.ingest.messages import Message


class _StubAdapter:
    """Minimal IngestAdapter stub that satisfies the Protocol."""

    fmt = "stub"

    def parse(self, raw: bytes) -> list[Message]:
        return [Message(
            speaker="X",
            timestamp=datetime(2026, 4, 21, 12, 0, tzinfo=UTC),
            text=raw.decode(),
        )]


def test_stub_adapter_satisfies_protocol() -> None:
    adapter: IngestAdapter = _StubAdapter()
    out = adapter.parse(b"hello")
    assert out[0].text == "hello"


def test_router_dispatches_to_registered_format() -> None:
    router = AdapterRouter()
    router.register("stub", _StubAdapter())
    msgs = router.parse("stub", b"hi")
    assert msgs[0].text == "hi"


def test_router_raises_for_unknown_format() -> None:
    router = AdapterRouter()
    with pytest.raises(UnknownFormatError):
        router.parse("nonexistent", b"")


def test_router_lists_supported_formats() -> None:
    router = AdapterRouter()
    router.register("stub", _StubAdapter())
    router.register("other", _StubAdapter())
    assert set(router.supported_formats()) == {"stub", "other"}
