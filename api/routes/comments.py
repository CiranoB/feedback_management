from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tornado.web import HTTPError

from api.routes.feedback import JsonHandler
from api.services.comments import CommentsService


class CommentCreate(BaseModel):
    author_id: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=10_000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: str
    content: str
    feedback_id: int


class CommentsHandler(JsonHandler):
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        database_engine: AsyncEngine = self.settings["database_engine"]
        return async_sessionmaker(database_engine, expire_on_commit=False)

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
