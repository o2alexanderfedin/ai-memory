"""Pydantic Settings env-var loader."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # type: ignore[explicit-any]
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://synthius:dev_only_password@localhost:5432/synthius_mem"
    )
    # app_database_url uses a non-superuser role so RLS is genuinely enforced.
    # Alembic migrations run via database_url (synthius/owner); the application
    # and integration tests connect via app_database_url (synthius_app).
    app_database_url: str = Field(
        default="postgresql+psycopg://synthius_app:dev_only_password@localhost:5432/synthius_mem"
    )
    jwt_secret: str = Field(default="dev_only_secret")
    zai_api_key: str = ""
    anthropic_api_key: str = ""
    otel_exporter_otlp_endpoint: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
