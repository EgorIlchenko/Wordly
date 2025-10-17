"""add verifier_hash to refresh_sessions

Revision ID: 2052eca47f52
Revises: d3a9333d8218
Create Date: 2025-08-18 06:06:08.854784

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2052eca47f52"
down_revision: Union[str, None] = "d3a9333d8218"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "refresh_sessions",
        sa.Column("verifier_hash", sa.String(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("refresh_sessions", "verifier_hash")
