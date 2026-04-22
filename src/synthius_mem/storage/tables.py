"""SQLAlchemy Core table defs (DIR-2.1, DIR-2.2, DIR-2.7).

We use Core (not ORM) because:
- ORM adds complexity without value here — we own the SQL via Alembic
- Hot retrieval path needs exact control over query shape (DIR-2.9)
"""
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

DOMAINS = ("biography", "experiences", "preferences",
           "social_circle", "work", "psychometrics")


def _domain_table(name: str) -> Table:
    return Table(
        name,
        metadata,
        Column("tenant_id", UUID(as_uuid=False), nullable=False),
        Column("persona_id", String(26), nullable=False),  # ULID = 26 chars (DIR-2.1)
        Column("fact_id", UUID(as_uuid=False), nullable=False),
        Column("schema_version", String, nullable=False),
        Column("fields", JSONB, nullable=False),
        Column("envelope", JSONB, nullable=False),
        Column("tombstoned_at", DateTime(timezone=True), nullable=True),
        Column("created_at", DateTime(timezone=True),
               server_default=text("now()"), nullable=False),
        Column("updated_at", DateTime(timezone=True),
               server_default=text("now()"), nullable=False),
        PrimaryKeyConstraint("tenant_id", "persona_id", "fact_id",
                             name=f"pk_{name}"),
        Index(f"ix_{name}_fields_gin", "fields",
              postgresql_using="gin",
              postgresql_ops={"fields": "jsonb_path_ops"}),
    )


for _domain in DOMAINS:
    _domain_table(_domain)


# WAL table (DIR-2.7)
wal = Table(
    "wal",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("persona_id", String(26), nullable=False),
    Column("seq", BigInteger, nullable=False),
    Column("op", Enum("add", "edit", "delete", "tombstone",
                      name="wal_op"), nullable=False),
    Column("domain", String, nullable=False),
    Column("fact_id", UUID(as_uuid=False), nullable=False),
    Column("delta", JSONB, nullable=False),
    Column("timestamp", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("extractor_version", String, nullable=False),
    Column("user_initiated", Boolean, nullable=False, server_default="false"),
    PrimaryKeyConstraint("tenant_id", "persona_id", "seq", name="pk_wal"),
)
