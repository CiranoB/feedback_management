from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.config.custom_exceptions import FeedbackNotFoundError
from api.models.comments import Comments


class CommentsService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_comments(self, *, feedback_id: int) -> Sequence[Comments]:
        async with self._session_factory() as session:
            comments = await session.scalars(
                select(Comments).where(Comments.feedback_id == feedback_id)
            )
            return list(comments)

    async def create_comment(
        self, *, author_id: str, content: str, feedback_id: int
    ) -> Comments:
        async with self._session_factory() as session:
            comment = Comments(
                author_id=author_id,
                content=content,
                feedback_id=feedback_id,
            )
            session.add(comment)
            try:
                await session.commit()
                await session.refresh(comment)
                return comment
            except IntegrityError as exc:
                raise FeedbackNotFoundError(
                    f"Feedback with id {feedback_id} does not exist"
                ) from exc
