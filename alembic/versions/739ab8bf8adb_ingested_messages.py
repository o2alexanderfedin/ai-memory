"""ingested_messages

Records the hash of every message an ingest job has processed, so a re-upload
skips all of them. pending_facts.source_hash only holds the first message of
each chunk, which let the rest of a re-uploaded conversation through again.

Revision ID: 739ab8bf8adb
Revises: dfc7bc40b15f
Create Date: 2026-10-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '739ab8bf8adb'
down_revision: Union[str, Sequence[str], None] = 'dfc7bc40b15f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('ingested_messages',
    sa.Column('tenant_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('persona_id', sa.String(length=26), nullable=False),
    sa.Column('message_hash', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'persona_id', 'message_hash', name='pk_ingested_messages')
    )

    op.execute("ALTER TABLE ingested_messages ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ingested_messages FORCE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY tenant_isolation ON ingested_messages
        USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
    """)
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ingested_messages TO ai_hive_app;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("REVOKE ALL ON ingested_messages FROM ai_hive_app;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON ingested_messages;")
    op.drop_table('ingested_messages')
