from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.feedback import Base, Feedback

if TYPE_CHECKING:
    from api.models.notation import Notation


def _notation_model() -> type[Notation]:
    from api.models.notation import Notation

    return Notation


class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id"), nullable=False)
    feedback: Mapped[Feedback] = relationship(back_populates="comments")
    notations: Mapped[list[Notation]] = relationship(
        _notation_model, back_populates="comment"
    )
