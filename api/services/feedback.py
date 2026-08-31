from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from api.config.custom_exceptions import FeedbackNotFoundError
from api.models.comments import Comments
from api.models.feedback import Feedback, FeedbackCategory, FeedbackStatus


class FeedbackService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_feedback(
        self, *, status: FeedbackStatus | None = None
    ) -> Sequence[Feedback]:
        async with self._session_factory() as session:
            query = select(Feedback).options(
                selectinload(Feedback.comments).selectinload(Comments.notations),
                selectinload(Feedback.notations),
            )
            if status is not None:
                query = query.where(Feedback.status == status)
            feedback_entries = await session.scalars(
                query.order_by(Feedback.id.desc())
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

    async def update_feedback(
        self,
        *,
        feedback_id: int,
        status: FeedbackStatus | None = None,
        category: FeedbackCategory | None = None,
    ) -> Feedback:
        values: dict[str, object] = {}
        if status is not None:
            values["status"] = status
        if category is not None:
            values["category"] = category

        async with self._session_factory() as session:
            result = await session.execute(
                update(Feedback)
                .where(Feedback.id == feedback_id)
                .values(**values)
                .returning(Feedback.id)
            )
            if result.scalar_one_or_none() is None:
                raise FeedbackNotFoundError(
                    f"Feedback with id {feedback_id} does not exist"
                )

            feedback = await session.scalar(
                select(Feedback)
                .options(
                    selectinload(Feedback.comments).selectinload(Comments.notations),
                    selectinload(Feedback.notations),
                )
                .where(Feedback.id == feedback_id)
            )
            await session.commit()
            assert feedback is not None
            return feedback

