"""Add current_availability table

Revision ID: a1b2c3d4e5f6
Revises: b7ff82388d46
Create Date: 2026-03-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b7ff82388d46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'current_availability',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('route_id', sa.String(), nullable=False),
        sa.Column('is_couchette', sa.Boolean(), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen_available_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('route_id', 'is_couchette', name='uq_current_availability_route_couchette')
    )
    op.create_index(op.f('ix_current_availability_route_id'), 'current_availability', ['route_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_current_availability_route_id'), table_name='current_availability')
    op.drop_table('current_availability')
    # Note: unique constraint uq_current_availability_route_couchette is dropped with the table
