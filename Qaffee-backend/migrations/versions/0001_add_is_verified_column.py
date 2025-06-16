"""Add is_verified column to users table

Revision ID: 0001
Revises: 
Create Date: 2025-06-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('users', 'is_verified')
