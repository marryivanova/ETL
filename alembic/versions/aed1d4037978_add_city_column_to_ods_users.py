"""add city column to ods_users

Revision ID: aed1d4037978
Revises: 1cb41b4aac2b
Create Date: 2025-08-01 16:55:34.010180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'aed1d4037978'
down_revision: Union[str, Sequence[str], None] = '1cb41b4aac2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('ods_users', sa.Column('city', sa.String(100)))


def downgrade():
    op.drop_column('ods_users', 'city')
