"""SQLAlchemy engine factory."""
from functools import lru_cache

from sqlalchemy import Engine, create_engine

from synthius_mem.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Return an engine that connects as the non-superuser app role.

    The app role (synthius_app) has no BYPASSRLS attribute, so RLS policies
    are genuinely enforced for all application and integration-test queries.
    Alembic migrations use database_url (synthius/owner) separately.
    """
    return create_engine(get_settings().app_database_url, future=True)
