"""create user model

Revision ID: e9f11e4b1e0e
Revises: 0deb7e2a7cbf
Create Date: 2025-07-27 13:05:21.483515

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e9f11e4b1e0e"
down_revision: Union[str, None] = "0deb7e2a7cbf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_google_account", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.drop_table("words")
    op.drop_table("user_words")
    op.drop_table("user_sessions")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "user_sessions",
        sa.Column("login", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "first_name", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "second_name", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text(
                "nextval('user_sessions_id_seq'::regclass)"
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_sessions"),
        sa.UniqueConstraint(
            "login",
            name="uq_user_sessions_login",
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "user_words",
        sa.Column(
            "user_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "word_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "is_learned", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "attempts", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "correct_attempts",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_sessions.id"],
            name=op.f("fk_user_words_user_id_user_sessions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["word_id"],
            ["words.id"],
            name=op.f("fk_user_words_word_id_words"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_words")),
    )
    op.create_table(
        "words",
        sa.Column(
            "text", sa.VARCHAR(length=64), autoincrement=False, nullable=False
        ),
        sa.Column(
            "translation",
            sa.VARCHAR(length=128),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "examples",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_words")),
        sa.UniqueConstraint(
            "text",
            name=op.f("uq_words_text"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
