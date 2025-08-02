from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = "77993181fb00"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("image", sa.Text),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("brand", sa.String(100)),
        sa.Column("model", sa.String(100)),
        sa.Column("color", sa.String(50), nullable=True),
        sa.Column("category", sa.String(100)),
        sa.Column("discount", sa.Integer, nullable=True),
        sa.Column("popular", sa.Boolean, nullable=True),
        sa.Column("on_sale", sa.Boolean, nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("name", JSONB, nullable=False),
        sa.Column("address", JSONB, nullable=False),
        sa.Column("phone", sa.String(50)),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("products")
