"""add most_expensive and ods_users tables

Revision ID: 1cb41b4aac2b
Revises: 77993181fb00
Create Date: 2025-08-01 16:33:40.423718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1cb41b4aac2b'
down_revision: Union[str, Sequence[str], None] = '77993181fb00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'most_expensive',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('category', sa.String(100), nullable=False)
    )

    op.create_table(
        'ods_users',
        sa.Column('user_id', sa.Integer, primary_key=True),
        sa.Column('firstname', sa.String(100), nullable=False),
        sa.Column('lastname', sa.String(100), nullable=False),
        sa.Column('lat', sa.Float),
        sa.Column('long', sa.Float),
        sa.Column('street_number', sa.String(50)),
        sa.Column('street', sa.String(255)),
        sa.Column('zipcode', sa.String(20))
    )


def downgrade():
    op.drop_table('ods_users')
    op.drop_table('most_expensive')
