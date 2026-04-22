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


# Tenants table — one row per tenant (DIR-11.1 + Decision 12 MVP)
tenants = Table(
    "tenants",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("created_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("tos_version", String, nullable=False),  # ToS version the tenant accepted at signup
    PrimaryKeyConstraint("tenant_id", name="pk_tenants"),
)


# Personas table — canonical persona record per (tenant, persona)
# (Domain-fact tables reference (tenant_id, persona_id) but don't FK; persona must
# exist here before any facts can be written — enforced at the application layer.)
personas = Table(
    "personas",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("persona_id", String(26), nullable=False),  # ULID
    Column("created_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("updated_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    PrimaryKeyConstraint("tenant_id", "persona_id", name="pk_personas"),
)


# Scope attestations — Decision 12 MVP customer-scope exclusions, recorded at signup
scope_attestations = Table(
    "scope_attestations",
    metadata,
    Column("tenant_id", UUID(as_uuid=False), nullable=False),
    Column("attested_at", DateTime(timezone=True),
           server_default=text("now()"), nullable=False),
    Column("no_phi", Boolean, nullable=False),
    Column("no_payment_data", Boolean, nullable=False),
    Column("no_minors", Boolean, nullable=False),
    Column("no_eu_uk_residents", Boolean, nullable=False),
    Column("no_sensitive_categories", Boolean, nullable=False),
    Column("source_ip", String(45), nullable=True),  # IPv4 or IPv6 string
    Column("source_country", String(2), nullable=True),  # ISO-3166 alpha-2 (or null)
    PrimaryKeyConstraint("tenant_id", name="pk_scope_attestations"),
)
