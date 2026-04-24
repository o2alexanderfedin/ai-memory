"""Shared test fixtures."""
from collections.abc import Generator  # noqa: F401

import pytest
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor  # noqa: F401

postgresql_proc = factories.postgresql_proc(port=None)
postgresql = factories.postgresql("postgresql_proc")


@pytest.fixture
def smoke() -> bool:
    return True
