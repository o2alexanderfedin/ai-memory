"""Shared test fixtures."""
from collections.abc import Generator  # noqa: F401

import pytest
from job_completion import JobCompletion, WaitDone
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor  # noqa: F401

from ai_hive_memory.api import conversations

postgresql_proc = factories.postgresql_proc(port=None)
postgresql = factories.postgresql("postgresql_proc")


@pytest.fixture
def smoke() -> bool:
    return True


@pytest.fixture
def wait_done(monkeypatch: pytest.MonkeyPatch) -> WaitDone:
    """Return `wait_done(client, token, job_id)` for ingest jobs started in this test."""
    completion = JobCompletion()
    monkeypatch.setattr(
        conversations, "_drive_pipeline", completion.wrap(conversations._drive_pipeline),
    )
    return completion.wait_done
