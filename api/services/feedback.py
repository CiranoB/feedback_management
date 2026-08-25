from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.models.feedback import Feedback


class FeedbackService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_feedback(self) -> Sequence[Feedback]:
        async with self._session_factory() as session:
            feedback_entries = await session.scalars(
                select(Feedback).order_by(Feedback.id.desc())
            )
            return list(feedback_entries)

    async def create_feedback(
        self, *, author_id: str, note: str | None, rating: int
    ) -> Feedback:
        async with self._session_factory() as session:
            feedback = Feedback(author_id=author_id, note=note, rating=rating)
            session.add(feedback)
            await session.commit()
            await session.refresh(feedback)
            return feedback
