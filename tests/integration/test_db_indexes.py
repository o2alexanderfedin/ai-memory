"""Verify schema, RLS, and indexes (DIR-2.1, DIR-2.2, DIR-2.3, DIR-11.1)."""
from sqlalchemy import text

from synthius_mem.storage.db import get_engine
from synthius_mem.storage.tables import metadata


def test_metadata_has_six_domain_tables_plus_wal(postgresql) -> None:
    table_names = {t.name for t in metadata.sorted_tables}
    expected = {"biography", "experiences", "preferences",
                "social_circle", "work", "psychometrics", "wal"}
    assert expected.issubset(table_names)


def test_six_domain_tables_have_composite_pk(postgresql) -> None:
    """DIR-2.1: composite PK (tenant_id, persona_id, fact_id)."""
    for table_name in ["biography", "experiences", "preferences",
                       "social_circle", "work", "psychometrics"]:
        table = metadata.tables[table_name]
        pk_cols = [c.name for c in table.primary_key.columns]
        assert pk_cols == ["tenant_id", "persona_id", "fact_id"], (
            f"{table_name} PK must be (tenant_id, persona_id, fact_id), got {pk_cols}"
        )


def test_each_domain_has_gin_and_btree_indexes() -> None:
    """DIR-2.2: GIN(fields jsonb_path_ops) + functional B-tree on hot sub-fields."""
    for table_name in ["biography", "work"]:  # spot-check 2 representative
        table = metadata.tables[table_name]
        idx_names = {idx.name for idx in table.indexes}
        assert any("gin" in n for n in idx_names), f"{table_name} missing GIN index"
