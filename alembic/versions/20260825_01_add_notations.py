"""Add author identifiers and feedback/comment notations.

Revision ID: 20260825_01
Revises: 20260824_01
Create Date: 2026-08-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260825_01"
down_revision: str | None = "20260824_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "feedback",
        sa.Column(
            "author_id",
            sa.String(length=255),
            nullable=False,
            server_default="legacy",
        ),
    )
    op.add_column(
        "comments",
        sa.Column(
            "author_id",
            sa.String(length=255),
            nullable=False,
            server_default="legacy",
        ),
    )
    op.alter_column("feedback", "author_id", server_default=None)
    op.alter_column("comments", "author_id", server_default=None)
    op.create_table(
        "notations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("feedback_id", sa.Integer(), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "(feedback_id IS NOT NULL AND comment_id IS NULL) OR "
            "(feedback_id IS NULL AND comment_id IS NOT NULL)",
            name="notation_single_target",
        ),
        sa.CheckConstraint("value BETWEEN -1 AND 1", name="notation_value_range"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"]),
        sa.ForeignKeyConstraint(["feedback_id"], ["feedback.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "comment_id", name="notation_user_comment"),
        sa.UniqueConstraint("user_id", "feedback_id", name="notation_user_feedback"),
    )


def downgrade() -> None:
    op.drop_table("notations")
    op.drop_column("comments", "author_id")
    op.drop_column("feedback", "author_id")