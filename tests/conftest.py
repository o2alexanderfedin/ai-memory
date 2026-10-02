"""Shared test fixtures."""
from collections.abc import Generator  # noqa: F401

import pytest
from job_completion import JobCompletion, WaitDone, WaitEnded
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor  # noqa: F401

from ai_hive_memory.api import conversations

postgresql_proc = factories.postgresql_proc(port=None)
postgresql = factories.postgresql("postgresql_proc")


@pytest.fixture
def smoke() -> bool:
    return True


@pytest.fixture
def job_completion(monkeypatch: pytest.MonkeyPatch) -> JobCompletion:
    """Signal the end of every ingest job's background pipeline started in this test."""
    completion = JobCompletion()
    monkeypatch.setattr(
        conversations, "_drive_pipeline", completion.wrap(conversations._drive_pipeline),
    )
    return completion


@pytest.fixture
def wait_done(job_completion: JobCompletion) -> WaitDone:
    """Return `wait_done(client, token, job_id)`: wait for the job, require DONE."""
    return job_completion.wait_done


@pytest.fixture
def wait_ended(job_completion: JobCompletion) -> WaitEnded:
    """Return `wait_ended(client, token, job_id)`: wait for the job, return its status."""
    return job_completion.wait_ended
