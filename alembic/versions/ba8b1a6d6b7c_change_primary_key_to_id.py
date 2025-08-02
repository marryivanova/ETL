"""change_primary_key_to_id

Revision ID: ba8b1a6d6b7c
Revises: aed1d4037978
Create Date: 2025-08-01 17:13:10.710319

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ba8b1a6d6b7c"
down_revision: Union[str, Sequence[str], None] = "aed1d4037978"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint("ods_users_pkey", "ods_users", type_="primary")

    op.add_column(
        "ods_users", sa.Column("id", sa.Integer, primary_key=True, autoincrement=True)
    )

    op.alter_column("ods_users", "user_id", existing_type=sa.INTEGER(), nullable=True)


def downgrade():
    op.drop_column("ods_users", "id")
    op.create_primary_key("ods_users_pkey", "ods_users", ["user_id"])
