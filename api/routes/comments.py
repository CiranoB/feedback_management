from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tornado.web import HTTPError

from api.models.notation import Notation
from api.routes.feedback import JsonHandler
from api.services.comments import CommentsService
from api.services.notation import NotationService


class CommentCreate(BaseModel):
    author_id: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=10_000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: str
    content: str
    feedback_id: int


class NotationCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=255)
    value: int = Field(ge=-1, le=1)


class NotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    value: int
    feedback_id: int | None
    comment_id: int | None


class DatabaseHandler(JsonHandler):
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        database_engine: AsyncEngine = self.settings["database_engine"]
        return async_sessionmaker(database_engine, expire_on_commit=False)

    async def create_notation(
        self, *, feedback_id: int | None = None, comment_id: int | None = None
    ) -> Notation:
        try:
            payload = NotationCreate.model_validate(json.loads(self.request.body))
        except (json.JSONDecodeError, ValidationError) as error:
            raise HTTPError(422, reason=f"Invalid notation payload: {error}") from error

        try:
            return await NotationService(self.session_factory).create_notation(
                user_id=payload.user_id,
                value=payload.value,
                feedback_id=feedback_id,
                comment_id=comment_id,
            )
        except IntegrityError as error:
            raise HTTPError(422, reason="Invalid or duplicate notation") from error


class CommentsHandler(DatabaseHandler):
    async def get(self, feedback_id: str) -> None:  # ty: ignore[invalid-method-override]
        comments = await CommentsService(self.session_factory).list_comments(
            feedback_id=int(feedback_id)
        )
        self.write(
            json.dumps(
                [
                    CommentResponse.model_validate(comment).model_dump()
                    for comment in comments
                ]
            )
        )

    async def post(self, feedback_id: str) -> None:  # ty: ignore[invalid-method-override]
        try:
            payload = CommentCreate.model_validate(json.loads(self.request.body))
        except (json.JSONDecodeError, ValidationError) as error:
            raise HTTPError(422, reason=f"Invalid comment payload: {error}") from error

        try:
            comment = await CommentsService(self.session_factory).create_comment(
                author_id=payload.author_id,
                content=payload.content,
                feedback_id=int(feedback_id),
            )
        except IntegrityError as error:
            raise HTTPError(422, reason="Feedback does not exist") from error

        self.set_status(201)
        self.write(CommentResponse.model_validate(comment).model_dump())


class FeedbackNotationHandler(DatabaseHandler):
    async def post(self, feedback_id: str) -> None:  # ty: ignore[invalid-method-override]
        notation = await self.create_notation(feedback_id=int(feedback_id))
        self.set_status(201)
        self.write(NotationResponse.model_validate(notation).model_dump())


class CommentNotationHandler(DatabaseHandler):
    async def post(self, comment_id: str) -> None:  # ty: ignore[invalid-method-override]
        notation = await self.create_notation(comment_id=int(comment_id))
        self.set_status(201)
        self.write(NotationResponse.model_validate(notation).model_dump())
