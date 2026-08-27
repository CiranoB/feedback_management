from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.config.custom_exceptions import DuplicateNotationError
from api.models.notation import Notation


class NotationService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create_notation(
        self,
        *,
        user_id: str,
        value: int,
        feedback_id: int | None = None,
        comment_id: int | None = None,
    ) -> Notation:
        async with self._session_factory() as session:
            notation = Notation(
                user_id=user_id,
                value=value,
                feedback_id=feedback_id,
                comment_id=comment_id,
            )
            session.add(notation)
            try:
                await session.commit()
                await session.refresh(notation)
                return notation
            except IntegrityError as exc:
                raise DuplicateNotationError(
                    "It is not possible to give more than one notation to a particular comment/feedback"
                ) from exc
