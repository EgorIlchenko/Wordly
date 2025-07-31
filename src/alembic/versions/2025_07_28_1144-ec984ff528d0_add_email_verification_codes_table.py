"""add email verification codes table

Revision ID: ec984ff528d0
Revises: 18048d287bf8
Create Date: 2025-07-28 11:44:35.625911

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ec984ff528d0"
down_revision: Union[str, None] = "18048d287bf8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "email_verification_codes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_email_verification_codes")
        ),
    )
    op.create_index(
        op.f("ix_email_verification_codes_id"),
        "email_verification_codes",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_email_verification_codes_email"),
        "email_verification_codes",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_email_verification_codes_id"),
        table_name="email_verification_codes",
    )
    op.drop_index(
        op.f("ix_email_verification_codes_email"),
        table_name="email_verification_codes",
    )
    op.drop_table("email_verification_codes")
