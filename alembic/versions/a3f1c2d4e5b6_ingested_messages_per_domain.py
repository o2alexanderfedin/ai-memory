"""ingested_messages per domain

Records, for each message, which extraction domains have processed it. A
chunk may be accepted with 5 of 6 domains (DIR-3.9); a re-upload must then
run the failed domain for those messages, and only that domain (US-2.3).

Rows written before this revision get domain '*', meaning every domain
processed the message, which is what such a row meant when it was written.

Revision ID: a3f1c2d4e5b6
Revises: 739ab8bf8adb
Create Date: 2026-10-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f1c2d4e5b6'
down_revision: Union[str, Sequence[str], None] = '739ab8bf8adb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('ingested_messages',
                  sa.Column('domain', sa.String(), nullable=False, server_default='*'))
    # Only existing rows get '*'; new rows must name their domain.
    op.alter_column('ingested_messages', 'domain', server_default=None)
    op.drop_constraint('pk_ingested_messages', 'ingested_messages', type_='primary')
    op.create_primary_key('pk_ingested_messages', 'ingested_messages',
                          ['tenant_id', 'persona_id', 'message_hash', 'domain'])


def downgrade() -> None:
    """Downgrade schema.

    Per-domain rows are dropped: after a downgrade, messages recorded only
    per domain count as not ingested and are extracted again.
    """
    op.execute("DELETE FROM ingested_messages WHERE domain <> '*';")
    op.drop_constraint('pk_ingested_messages', 'ingested_messages', type_='primary')
    op.drop_column('ingested_messages', 'domain')
    op.create_primary_key('pk_ingested_messages', 'ingested_messages',
                          ['tenant_id', 'persona_id', 'message_hash'])
