"""Regression tests exercising `FeedbackService.merge_feedback` against a real
SQLAlchemy session (in-memory SQLite) so that database-level check constraints
are actually enforced, unlike the mocked-session unit tests in
`test_feedback.py`.
"""

import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from api.models.feedback import Base, Feedback
from api.models.notation import Notation
from api.services.feedback import FeedbackService


async def _create_engine() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    return engine


def test_merge_feedback_moves_notations_without_violating_check_constraint() -> None:
    """Two feedback entries with a notation from the same user used to raise a
    CheckViolationError on `notation_single_target` because reassigning
    `Notation.feedback_id` directly left the stale ORM `notations` collection on
    the deleted source feedback, causing SQLAlchemy to null the FK on flush.
    """

    async def scenario() -> Feedback:
        engine = await _create_engine()
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            target = Feedback(author_id="user-1", note="Text 1", rating=5)
            source = Feedback(author_id="user-2", note="Text 2", rating=3)
            session.add_all([target, source])
            await session.commit()

            session.add_all(
                [
                    Notation(user_id="shared-user", value=1, feedback_id=target.id),
                    Notation(user_id="shared-user", value=-1, feedback_id=source.id),
                    Notation(user_id="other-user", value=1, feedback_id=source.id),
                ]
            )
            await session.commit()
            target_id, source_id = target.id, source.id

        service = FeedbackService(session_factory)
        return await service.merge_feedback(
            source_feedback_id=source_id, target_feedback_id=target_id
        )

    merged = asyncio.run(scenario())

    notations_by_user = {notation.user_id: notation for notation in merged.notations}
    assert set(notations_by_user) == {"shared-user", "other-user"}
    # Target's notation wins on conflict: value stays 1, not source's -1.
    assert notations_by_user["shared-user"].value == 1
    assert notations_by_user["shared-user"].feedback_id == merged.id
    assert notations_by_user["other-user"].feedback_id == merged.id
