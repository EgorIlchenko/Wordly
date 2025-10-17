"""make user password nullable

Revision ID: bdcafc8d8402
Revises: a09782f1b84e
Create Date: 2025-08-25 05:42:14.797652

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bdcafc8d8402"
down_revision: Union[str, None] = "a09782f1b84e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users", "hashed_password", existing_type=sa.VARCHAR(), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users", "hashed_password", existing_type=sa.VARCHAR(), nullable=False
    )
