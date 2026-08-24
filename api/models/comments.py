from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.feedback import Base, Feedback


class Comments(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedback.id"), nullable=False)
    feedback: Mapped[Feedback] = relationship(back_populates="comments")
