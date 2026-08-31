"""Add feedback category.

Revision ID: 20260831_01
Revises: 20260825_01
Create Date: 2026-08-31
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260831_01"
down_revision: str | None = "20260825_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "feedback",
        sa.Column(
            "category",
            sa.Enum(
                "FRONTEND",
                "BACKEND",
                "PERFORMANCE_ISSUES",
                "BUGS",
                name="feedback_category",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("feedback", "category")
