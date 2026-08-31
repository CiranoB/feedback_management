import asyncio
from collections.abc import Callable
from unittest.mock import AsyncMock, Mock

import pytest

from api.config.custom_exceptions import FeedbackMergeError, FeedbackNotFoundError
from api.models.feedback import Feedback, FeedbackCategory, FeedbackStatus
from api.models.notation import Notation
from api.services.feedback import FeedbackService


def test_list_feedback_returns_feedback_entries(
    make_session: Callable[..., Mock],
) -> None:
    feedback_entries = [
        Feedback(id=1, author_id="user-1", note="note", rating=5),
        Feedback(id=2, author_id="user-2", note=None, rating=3),
    ]
    session = make_session(scalars_return_value=feedback_entries)
    service = FeedbackService(_session_factory(session))

    result = asyncio.run(service.list_feedback())

    assert result == feedback_entries
    session.scalars.assert_awaited_once()


def test_list_feedback_filters_by_status(
    make_session: Callable[..., Mock],
) -> None:
    feedback_entries = [
        Feedback(
            id=1, author_id="user-1", note="note", rating=5, status=FeedbackStatus.OPEN
        )
    ]
    session = make_session(scalars_return_value=feedback_entries)
    service = FeedbackService(_session_factory(session))

    result = asyncio.run(service.list_feedback(status=FeedbackStatus.OPEN))

    assert result == feedback_entries
    session.scalars.assert_awaited_once()


def test_create_feedback_creates_new_feedback(
    make_session: Callable[..., Mock],
) -> None:
    session = make_session()
    service = FeedbackService(_session_factory(session))

    feedback = asyncio.run(
        service.create_feedback(author_id="user-1", note="note", rating=4)
    )

    assert feedback.author_id == "user-1"
    assert feedback.note == "note"
    assert feedback.rating == 4
    session.add.assert_called_once_with(feedback)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(feedback)


def test_update_feedback_updates_status(
    make_session: Callable[..., Mock],
) -> None:
    feedback = Feedback(
        id=1, author_id="user-1", note="note", rating=5, status=FeedbackStatus.OPEN
    )
    session = make_session(
        execute_return_value=_execute_result(1),
        scalar_return_value=feedback,
    )
    service = FeedbackService(_session_factory(session))

    updated = asyncio.run(
        service.update_feedback(feedback_id=1, status=FeedbackStatus.CLOSED_SOLVED)
    )

    assert updated is feedback
    session.execute.assert_awaited_once()
    session.scalar.assert_awaited_once()
    session.commit.assert_awaited_once()


def test_update_feedback_updates_category(
    make_session: Callable[..., Mock],
) -> None:
    feedback = Feedback(
        id=1, author_id="user-1", note="note", rating=5, category=FeedbackCategory.BUGS
    )
    session = make_session(
        execute_return_value=_execute_result(1),
        scalar_return_value=feedback,
    )
    service = FeedbackService(_session_factory(session))

    updated = asyncio.run(
        service.update_feedback(feedback_id=1, category=FeedbackCategory.BUGS)
    )

    assert updated is feedback
    session.execute.assert_awaited_once()
    session.scalar.assert_awaited_once()
    session.commit.assert_awaited_once()


def test_update_feedback_raises_when_feedback_does_not_exist(
    make_session: Callable[..., Mock],
) -> None:
    session = make_session(execute_return_value=_execute_result(None))
    service = FeedbackService(_session_factory(session))

    with pytest.raises(FeedbackNotFoundError):
        asyncio.run(
            service.update_feedback(feedback_id=1, status=FeedbackStatus.CLOSED_SOLVED)
        )

    session.scalar.assert_not_awaited()
    session.commit.assert_not_awaited()


def test_merge_feedback_combines_notes_and_moves_comments(
    make_session: Callable[..., Mock],
) -> None:
    source = Feedback(id=2, author_id="user-2", note="Text 2", rating=3)
    target = Feedback(
        id=1,
        author_id="user-1",
        note="Text 1",
        rating=5,
        status=FeedbackStatus.CLOSED_SOLVED,
        category=FeedbackCategory.BUGS,
    )
    merged = Feedback(
        id=1,
        author_id="user-1",
        note="Text 1\n-----\nText 2",
        rating=5,
        status=FeedbackStatus.CLOSED_SOLVED,
        category=FeedbackCategory.BUGS,
    )
    session = make_session()
    session.scalar = AsyncMock(side_effect=[source, target, merged])
    service = FeedbackService(_session_factory(session))

    result = asyncio.run(
        service.merge_feedback(source_feedback_id=2, target_feedback_id=1)
    )

    assert result is merged
    assert target.note == "Text 1\n-----\nText 2"
    session.execute.assert_awaited_once()
    session.delete.assert_awaited_once_with(source)
    session.commit.assert_awaited_once()


def test_merge_feedback_uses_source_note_when_target_note_is_none(
    make_session: Callable[..., Mock],
) -> None:
    source = Feedback(id=2, author_id="user-2", note="Text 2", rating=3)
    target = Feedback(id=1, author_id="user-1", note=None, rating=5)
    session = make_session()
    session.scalar = AsyncMock(side_effect=[source, target, target])
    service = FeedbackService(_session_factory(session))

    asyncio.run(service.merge_feedback(source_feedback_id=2, target_feedback_id=1))

    assert target.note == "Text 2"


def test_merge_feedback_keeps_target_note_when_source_note_is_none(
    make_session: Callable[..., Mock],
) -> None:
    source = Feedback(id=2, author_id="user-2", note=None, rating=3)
    target = Feedback(id=1, author_id="user-1", note="Text 1", rating=5)
    session = make_session()
    session.scalar = AsyncMock(side_effect=[source, target, target])
    service = FeedbackService(_session_factory(session))

    asyncio.run(service.merge_feedback(source_feedback_id=2, target_feedback_id=1))

    assert target.note == "Text 1"


def test_merge_feedback_drops_source_notation_on_conflict(
    make_session: Callable[..., Mock],
) -> None:
    conflicting_notation = Notation(id=10, user_id="user-a", value=1, feedback_id=2)
    movable_notation = Notation(id=11, user_id="user-b", value=-1, feedback_id=2)
    source = Feedback(
        id=2,
        author_id="user-2",
        note="Text 2",
        rating=3,
        notations=[conflicting_notation, movable_notation],
    )
    target = Feedback(
        id=1,
        author_id="user-1",
        note="Text 1",
        rating=5,
        notations=[Notation(id=12, user_id="user-a", value=0, feedback_id=1)],
    )
    session = make_session()
    session.scalar = AsyncMock(side_effect=[source, target, target])
    service = FeedbackService(_session_factory(session))

    asyncio.run(service.merge_feedback(source_feedback_id=2, target_feedback_id=1))

    session.delete.assert_any_await(conflicting_notation)
    assert movable_notation.feedback_id == 1


def test_merge_feedback_raises_when_source_does_not_exist(
    make_session: Callable[..., Mock],
) -> None:
    session = make_session()
    session.scalar = AsyncMock(return_value=None)
    service = FeedbackService(_session_factory(session))

    with pytest.raises(FeedbackNotFoundError):
        asyncio.run(service.merge_feedback(source_feedback_id=2, target_feedback_id=1))

    session.commit.assert_not_awaited()


def test_merge_feedback_raises_when_target_does_not_exist(
    make_session: Callable[..., Mock],
) -> None:
    source = Feedback(id=2, author_id="user-2", note="Text 2", rating=3)
    session = make_session()
    session.scalar = AsyncMock(side_effect=[source, None])
    service = FeedbackService(_session_factory(session))

    with pytest.raises(FeedbackNotFoundError):
        asyncio.run(service.merge_feedback(source_feedback_id=2, target_feedback_id=1))

    session.commit.assert_not_awaited()


def test_merge_feedback_raises_when_merging_into_itself() -> None:
    service = FeedbackService(Mock())

    with pytest.raises(FeedbackMergeError):
        asyncio.run(service.merge_feedback(source_feedback_id=1, target_feedback_id=1))


def _execute_result(value: int | None) -> Mock:
    return Mock(scalar_one_or_none=Mock(return_value=value))


def _session_factory(*sessions: Mock) -> Mock:
    session_iterator = iter(sessions)
    session_factory = Mock()
    session_factory.side_effect = lambda: next(session_iterator)
    return session_factory
