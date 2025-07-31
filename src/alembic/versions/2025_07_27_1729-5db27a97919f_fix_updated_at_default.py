"""Fix updated_at default

Revision ID: 5db27a97919f
Revises: 72108d98e173
Create Date: 2025-07-27 17:29:01.619701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5db27a97919f"
down_revision: Union[str, None] = "72108d98e173"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "updated_at",
        server_default=sa.text("now()"),
        existing_type=sa.TIMESTAMP(timezone=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "updated_at",
        server_default=None,
        existing_type=sa.TIMESTAMP(timezone=True),
    )
