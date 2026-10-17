"""add_source_id_to_events

Revision ID: f9b4fe1eda98
Revises: 31b8aee46d2d
Create Date: 2026-10-17 13:41:59.092827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9b4fe1eda98'
down_revision: Union[str, Sequence[str], None] = '31b8aee46d2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('chunks', sa.Column('chunk_index', sa.Integer(), nullable=False))
    op.add_column('events', sa.Column('source_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_events_source_id'), 'events', ['source_id'], unique=False)
    op.create_foreign_key('fk_events_source_id_sources', 'events', 'sources', ['source_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_events_source_id_sources', 'events', type_='foreignkey')
    op.drop_index(op.f('ix_events_source_id'), table_name='events')
    op.drop_column('events', 'source_id')
    op.drop_column('chunks', 'chunk_index')