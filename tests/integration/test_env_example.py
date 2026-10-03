"""`.env.example` names database accounts that really exist.

A user starts by copying `.env.example` to `.env`. The service then connects
with APP_DATABASE_URL, so that role must be the one the migrations create,
with the password they give it. The owner account in DATABASE_URL must be
the one docker-compose.yml gives its Postgres.
"""
import re
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from ai_hive_memory.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[2]


def _example_url(name: str) -> URL:
    for line in (REPO_ROOT / ".env.example").read_text().splitlines():
        key, _, value = line.partition("=")
        if key.strip() == name:
            return make_url(value.strip())
    raise AssertionError(f"{name} is missing from .env.example")


def _compose_postgres_env(name: str) -> str:
    compose = (REPO_ROOT / "docker-compose.yml").read_text()
    match = re.search(rf"^\s+{name}:\s*(\S+)\s*$", compose, re.MULTILINE)
    assert match is not None, f"{name} is missing from docker-compose.yml"
    return match.group(1)


def test_example_app_account_can_read_the_migrated_schema() -> None:
    example = _example_url("APP_DATABASE_URL")
    # Same server and database as the tests use; account from .env.example.
    url = make_url(get_settings().app_database_url).set(
        username=example.username, password=example.password,
    )
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT count(*) FROM tenants")).scalar_one()
    finally:
        engine.dispose()


def test_example_owner_account_matches_docker_compose() -> None:
    example = _example_url("DATABASE_URL")
    assert example.username == _compose_postgres_env("POSTGRES_USER")
    assert example.password == _compose_postgres_env("POSTGRES_PASSWORD")
    assert example.database == _compose_postgres_env("POSTGRES_DB")
    app = _example_url("APP_DATABASE_URL")
    assert app.database == example.database
