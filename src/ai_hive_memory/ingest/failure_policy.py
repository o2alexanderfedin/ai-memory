"""ExtractionFailurePolicy — exponential-backoff retry, DLQ, partial-accept (US-2.7 DIR-3.9)."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TypeVar

MIN_PARTIAL_ACCEPT_DOMAINS = 5

T = TypeVar("T")


class PartialAcceptError(Exception):
    """Raised when too few domains succeeded to satisfy the partial-accept threshold."""


@dataclass
class DeadLetterEntry:
    """One failed domain extraction stored in the dead-letter queue."""

    domain: str
    error: Exception
    attempts: int


@dataclass
class ExtractionFailurePolicy:
    """Retry with exponential back-off; failed domains go to the DLQ.

    Accepts facts from a chunk even if some domains fail, provided at least
    MIN_PARTIAL_ACCEPT_DOMAINS (5) of 6 succeed (DIR-3.9).
    """

    max_attempts: int = 3
    base_delay_s: float = 0.5
    factor: float = 2.0
    dlq: list[DeadLetterEntry] = field(default_factory=list)

    async def run(self, domain: str, fn: Callable[[], T]) -> T:
        """Run a synchronous callable with retry; on exhaustion append DLQ and reraise."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except Exception as exc:
                last_exc = exc
                if attempt < self.max_attempts:
                    delay = self.base_delay_s * (self.factor ** (attempt - 1))
                    await asyncio.sleep(delay)

        assert last_exc is not None
        self.dlq.append(
            DeadLetterEntry(domain=domain, error=last_exc, attempts=self.max_attempts)
        )
        raise last_exc

    async def run_async(self, domain: str, fn: Callable[[], Awaitable[T]]) -> T:
        """Run an async callable with retry; on exhaustion append DLQ and reraise."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await fn()
            except Exception as exc:
                last_exc = exc
                if attempt < self.max_attempts:
                    delay = self.base_delay_s * (self.factor ** (attempt - 1))
                    await asyncio.sleep(delay)

        assert last_exc is not None
        self.dlq.append(
            DeadLetterEntry(domain=domain, error=last_exc, attempts=self.max_attempts)
        )
        raise last_exc

    @staticmethod
    def assert_partial_accept(
        succeeded_domains: list[str],
        all_domains: list[str],
    ) -> None:
        """Raise PartialAcceptError if fewer than MIN_PARTIAL_ACCEPT_DOMAINS succeeded."""
        if len(succeeded_domains) < MIN_PARTIAL_ACCEPT_DOMAINS:
            missing = sorted(set(all_domains) - set(succeeded_domains))
            raise PartialAcceptError(
                f"only {len(succeeded_domains)}/{len(all_domains)} domains succeeded; "
                f"missing: {missing}"
            )
