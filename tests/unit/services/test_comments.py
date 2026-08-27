import asyncio
from collections.abc import Callable
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from api.config.custom_exceptions import FeedbackNotFoundError
from api.models.comments import Comments
from api.services.comments import CommentsService


def test_list_comments_returns_comments_for_feedback(
    make_session: Callable[..., Mock],
) -> None:
    comments = [
        Comments(id=1, author_id="user-1", content="content", feedback_id=1),
        Comments(id=2, author_id="user-2", content="other content", feedback_id=1),
    ]
    session = make_session(scalars_return_value=comments)
    service = CommentsService(_session_factory(session))

    result = asyncio.run(service.list_comments(feedback_id=1))

    assert result == comments
    session.scalars.assert_awaited_once()


def test_create_comment_creates_new_comment(
    make_session: Callable[..., Mock],
) -> None:
    session = make_session()
    service = CommentsService(_session_factory(session))

    comment = asyncio.run(
        service.create_comment(author_id="user-1", content="content", feedback_id=1)
    )

    assert comment.author_id == "user-1"
    assert comment.content == "content"
    assert comment.feedback_id == 1
    session.add.assert_called_once_with(comment)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(comment)


def test_create_comment_raises_when_feedback_does_not_exist(
    make_session: Callable[..., Mock],
) -> None:
    session = make_session(
        commit_side_effect=IntegrityError(
            "statement", {}, Exception("foreign key violation")
        )
    )
    service = CommentsService(_session_factory(session))

    with pytest.raises(FeedbackNotFoundError):
        asyncio.run(
            service.create_comment(author_id="user-1", content="content", feedback_id=1)
        )

    session.refresh.assert_not_awaited()


def _session_factory(*sessions: Mock) -> Mock:
    session_iterator = iter(sessions)
    session_factory = Mock()
    session_factory.side_effect = lambda: next(session_iterator)
    return session_factory
