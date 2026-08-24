"""Create the feedback schema.

Revision ID: 20260824_01
Revises:
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260824_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "OPEN",
                "CLOSED_BACKLOG",
                "CLOSED_SOLVED",
                "CLOSED_REJECTED",
                name="feedback_status",
                native_enum=False,
                create_constraint=True,
            ),
            server_default="OPEN",
            nullable=False,
        ),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="feedback_rating_range"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("feedback_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["feedback_id"], ["feedback.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("comments")
    op.drop_table("feedback")
