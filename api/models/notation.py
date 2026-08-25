from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.comments import Comments
from api.models.feedback import Base, Feedback


class Notation(Base):
    __tablename__ = "notations"
    __table_args__ = (
        CheckConstraint(
            "(feedback_id IS NOT NULL AND comment_id IS NULL) OR "
            "(feedback_id IS NULL AND comment_id IS NOT NULL)",
            name="notation_single_target",
        ),
        UniqueConstraint("user_id", "feedback_id", name="notation_user_feedback"),
        UniqueConstraint("user_id", "comment_id", name="notation_user_comment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("value BETWEEN -1 AND 1", name="notation_value_range"),
        nullable=False,
    )
    feedback_id: Mapped[int | None] = mapped_column(ForeignKey("feedback.id"))
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    feedback: Mapped[Feedback | None] = relationship(back_populates="notations")
    comment: Mapped[Comments | None] = relationship(back_populates="notations")
