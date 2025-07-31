"""Add is_subscribed field to users

Revision ID: 18048d287bf8
Revises: 5db27a97919f
Create Date: 2025-07-28 09:26:46.236266

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "18048d287bf8"
down_revision: Union[str, None] = "5db27a97919f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("is_subscribed", sa.Boolean(), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_subscribed")
