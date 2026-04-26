"""ExtractionFailurePolicy — retry, DLQ, 5/6 partial-accept (US-2.7 DIR-3.9)."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from ai_hive_memory.ingest.failure_policy import (
    ExtractionFailurePolicy,
    PartialAcceptError,
)


@pytest.mark.asyncio
async def test_run_succeeds_on_first_attempt() -> None:
    """Callable that succeeds immediately returns its value without retries."""
    policy = ExtractionFailurePolicy()

    def _fn() -> str:
        return "ok"

    result = await policy.run("biography", _fn)
    assert result == "ok"
    assert policy.dlq == []


@pytest.mark.asyncio
async def test_run_retries_then_appends_dlq_on_final_failure() -> None:
    """Callable that always fails: retried max_attempts times, then added to DLQ."""
    policy = ExtractionFailurePolicy(max_attempts=3, base_delay_s=0.5)

    calls: list[int] = []

    def _always_fail() -> str:
        calls.append(1)
        raise RuntimeError("boom")

    with (
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        pytest.raises(RuntimeError, match="boom"),
    ):
        await policy.run("biography", _always_fail)

    max_att = policy.max_attempts
    assert len(calls) == max_att
    assert len(policy.dlq) == 1
    assert policy.dlq[0].domain == "biography"
    assert policy.dlq[0].attempts == max_att
    # exponential backoff: one sleep per retry gap (max_attempts - 1)
    assert mock_sleep.call_count == max_att - 1


@pytest.mark.asyncio
async def test_run_async_succeeds_on_first_attempt() -> None:
    """Async callable that succeeds immediately returns its value."""
    policy = ExtractionFailurePolicy()

    async def _fn() -> str:
        return "async_ok"

    result = await policy.run_async("work", _fn)
    assert result == "async_ok"
    assert policy.dlq == []


_ALL_DOMAINS = [
    "biography", "experiences", "preferences", "social_circle", "work", "psychometrics"
]


def test_assert_partial_accept_raises_when_fewer_than_5_domains_succeeded() -> None:
    """Raises PartialAcceptError when fewer than 5 of 6 domains succeeded."""
    succeeded = ["biography", "experiences", "preferences", "social_circle"]  # only 4
    with pytest.raises(PartialAcceptError):
        ExtractionFailurePolicy.assert_partial_accept(succeeded, _ALL_DOMAINS)


def test_assert_partial_accept_passes_when_5_or_more_domains_succeeded() -> None:
    """Does not raise when 5 or more of 6 domains succeeded."""
    succeeded = ["biography", "experiences", "preferences", "social_circle", "work"]
    # Should not raise
    ExtractionFailurePolicy.assert_partial_accept(succeeded, _ALL_DOMAINS)
