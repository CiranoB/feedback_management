import asyncio
from collections.abc import Callable
from unittest.mock import Mock

import pytest

from api.config.custom_exceptions import FeedbackNotFoundError
from api.models.feedback import Feedback, FeedbackCategory, FeedbackStatus
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



def _execute_result(value: int | None) -> Mock:
    return Mock(scalar_one_or_none=Mock(return_value=value))


def _session_factory(*sessions: Mock) -> Mock:
    session_iterator = iter(sessions)
    session_factory = Mock()
    session_factory.side_effect = lambda: next(session_iterator)
    return session_factory
