"""create password reset tokens table

Revision ID: ff0a3003c20f
Revises: bdcafc8d8402
Create Date: 2025-08-31 09:07:02.549892

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ff0a3003c20f"
down_revision: Union[str, None] = "bdcafc8d8402"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "password_reset_tokens",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("hashed_token", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_password_reset_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_password_reset_tokens")),
        sa.UniqueConstraint(
            "user_id", name=op.f("uq_password_reset_tokens_user_id")
        ),
    )
    op.create_index(
        op.f("ix_password_reset_tokens_hashed_token"),
        "password_reset_tokens",
        ["hashed_token"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_tokens_id"),
        "password_reset_tokens",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_password_reset_tokens_id"), table_name="password_reset_tokens"
    )
    op.drop_index(
        op.f("ix_password_reset_tokens_hashed_token"),
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")
