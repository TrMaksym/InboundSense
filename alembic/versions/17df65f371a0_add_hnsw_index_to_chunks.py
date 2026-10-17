"""add_hnsw_index_to_chunks

Revision ID: 17df65f371a0
Revises: 6a6f0cad320a
Create Date: 2026-10-17 18:15:59.794212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17df65f371a0'
down_revision: Union[str, None] = '6a6f0cad320a' # переконайся, що посилається на попередню міграцію
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx 
        ON chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw_idx;")