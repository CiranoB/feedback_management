from collections.abc import Callable
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def make_session() -> Callable[..., Mock]:
    def create_session(
        *,
        commit_side_effect: Exception | None = None,
        scalar_return_value: object | None = None,
        scalars_return_value: object | None = None,
        execute_return_value: object | None = None,
    ) -> Mock:
        session = Mock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        session.add = Mock()
        session.commit = AsyncMock(side_effect=commit_side_effect)
        session.refresh = AsyncMock()
        session.scalar = AsyncMock(return_value=scalar_return_value)
        session.scalars = AsyncMock(return_value=scalars_return_value)
        session.execute = AsyncMock(return_value=execute_return_value)
        return session

    return create_session


@pytest.fixture
def make_duplicate_sessions(
    make_session: Callable[..., Mock],
) -> Callable[..., tuple[Mock, Mock]]:
    def create_sessions() -> tuple[Mock, Mock]:
        successful_session = make_session()
        duplicate_session = make_session(
            commit_side_effect=IntegrityError(
                "statement", {}, Exception("unique violation")
            )
        )
        return successful_session, duplicate_session

    return create_sessions
