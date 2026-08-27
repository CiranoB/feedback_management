import asyncio
from collections.abc import Callable
from unittest.mock import Mock

import pytest

from api.config.custom_exceptions import DuplicateNotationError
from api.services.notation import NotationService


def test_create_notation_creates_one_feedback_notation(
    make_session: Callable[..., Mock],
) -> None:
    session = make_session()
    service = NotationService(_session_factory(session))

    notation = asyncio.run(
        service.create_notation(user_id="user-1", value=1, feedback_id=1)
    )

    assert notation.user_id == "user-1"
    assert notation.value == 1
    assert notation.feedback_id == 1
    assert notation.comment_id is None
    session.add.assert_called_once_with(notation)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(notation)


@pytest.mark.parametrize("id_field", ["feedback_id", "comment_id"])
def test_create_notation_raises_when_user_duplicates_notation(
    id_field: str,
    make_duplicate_sessions: Callable[..., tuple[Mock, Mock]],
) -> None:
    service = NotationService(_session_factory(*make_duplicate_sessions()))

    async def create_duplicate_notation() -> None:
        await service.create_notation(user_id="user-1", value=1, **{id_field: 1})
        await service.create_notation(user_id="user-1", value=-1, **{id_field: 1})

    with pytest.raises(DuplicateNotationError):
        asyncio.run(create_duplicate_notation())


def _session_factory(*sessions: Mock) -> Mock:
    session_iterator = iter(sessions)
    session_factory = Mock()
    session_factory.side_effect = lambda: next(session_iterator)
    return session_factory
