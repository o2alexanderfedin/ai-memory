"""SQLAlchemy engine factory."""
from functools import lru_cache

from sqlalchemy import Engine, create_engine

from synthius_mem.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, future=True)
