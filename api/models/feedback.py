from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from api.models.comments import Comments
    from api.models.notation import Notation


def _notation_model() -> type[Notation]:
    from api.models.notation import Notation

    return Notation


class Base(DeclarativeBase):
    pass


class FeedbackStatus(str, Enum):
    OPEN = "open"
    CLOSED_BACKLOG = "closed_backlog"
    CLOSED_SOLVED = "closed_solved"
    CLOSED_REJECTED = "closed_rejected"


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint(sqltext="rating BETWEEN 1 AND 5", name="feedback_rating_range"),
        nullable=False,
    )
    status: Mapped[FeedbackStatus] = mapped_column(
        SqlEnum(
            FeedbackStatus,
            name="feedback_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        default=FeedbackStatus.OPEN,
        server_default=FeedbackStatus.OPEN.name,
        nullable=False,
    )
    comments: Mapped[list[Comments]] = relationship(back_populates="feedback")
    notations: Mapped[list[Notation]] = relationship(
        _notation_model, back_populates="feedback"
    )
