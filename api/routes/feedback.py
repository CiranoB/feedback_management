from __future__ import annotations

import json
from collections.abc import Sequence
from urllib.parse import quote

from pydantic import BaseModel, Field, ValidationError, model_validator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tornado.web import HTTPError, RequestHandler

from api.config.custom_exceptions import FeedbackNotFoundError
from api.config.global_settings import settings
from api.models.comments import Comments
from api.models.feedback import Feedback, FeedbackCategory, FeedbackStatus
from api.models.notation import Notation
from api.services.feedback import FeedbackService


class FeedbackCreate(BaseModel):
    author_id: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=10_000)
    rating: int = Field(ge=1, le=5)


class FeedbackManagerUpdate(BaseModel):
    status: FeedbackStatus | None = None
    category: FeedbackCategory | None = None

    @model_validator(mode="after")
    def _require_at_least_one_field(self) -> FeedbackManagerUpdate:
        if self.status is None and self.category is None:
            raise ValueError("At least one of status or category must be provided")
        return self


class NotationSummary(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0

    @classmethod
    def from_notations(cls, notations: Sequence[Notation]) -> NotationSummary:
        return cls(
            positive=sum(notation.value == 1 for notation in notations),
            neutral=sum(notation.value == 0 for notation in notations),
            negative=sum(notation.value == -1 for notation in notations),
        )


class CommentResponse(BaseModel):
    id: int
    author_id: str
    content: str
    feedback_id: int
    notations: NotationSummary

    @classmethod
    def from_model(cls, comment: Comments) -> CommentResponse:
        return cls(
            id=comment.id,
            author_id=comment.author_id,
            content=comment.content,
            feedback_id=comment.feedback_id,
            notations=NotationSummary.from_notations(comment.notations),
        )


class UserFeedbackResponse(BaseModel):
    id: int
    note: str | None
    rating: int
    comments: list[CommentResponse]
    notations: NotationSummary

    @classmethod
    def from_model(cls, feedback: Feedback) -> UserFeedbackResponse:
        return cls(
            id=feedback.id,
            note=feedback.note,
            rating=feedback.rating,
            comments=[
                CommentResponse.from_model(comment) for comment in feedback.comments
            ],
            notations=NotationSummary.from_notations(feedback.notations),
        )


class ProductManagerFeedbackResponse(UserFeedbackResponse):
    author_id: str
    status: FeedbackStatus
    category: FeedbackCategory | None

    @classmethod
    def from_model(cls, feedback: Feedback) -> ProductManagerFeedbackResponse:
        return cls(
            id=feedback.id,
            author_id=feedback.author_id,
            note=feedback.note,
            rating=feedback.rating,
            status=feedback.status,
            category=feedback.category,
            comments=[
                CommentResponse.from_model(comment) for comment in feedback.comments
            ],
            notations=NotationSummary.from_notations(feedback.notations),
        )


WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class JsonHandler(RequestHandler):
    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "application/json")

    def prepare(self) -> None:
        if (
            self.request.method in WRITE_METHODS
            and self.request.headers.get("X-API-Key") != settings.auth_token
        ):
            raise HTTPError(401, reason="Unauthorized")

    def write_error(self, status_code: int, **kwargs: object) -> None:
        self.finish({"detail": self._reason})


class FeedbackHandler(JsonHandler):
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        database_engine: AsyncEngine = self.settings["database_engine"]
        return async_sessionmaker(database_engine, expire_on_commit=False)

    async def get(self, *args: str, **kwargs: str) -> None:  # ty: ignore[invalid-method-override]
        feedback_entries = await FeedbackService(self.session_factory).list_feedback()
        response = [
            UserFeedbackResponse.from_model(entry).model_dump(mode="json")
            for entry in feedback_entries
        ]
        self.write(json.dumps(response))

    async def post(self, *args: str, **kwargs: str) -> None:  # ty: ignore[invalid-method-override]
        try:
            payload: FeedbackCreate = FeedbackCreate.model_validate(
                json.loads(self.request.body)
            )
        except (json.JSONDecodeError, ValidationError) as error:
            raise HTTPError(422, reason=f"Invalid feedback payload: {error}") from error

        feedback = await FeedbackService(self.session_factory).create_feedback(
            author_id=payload.author_id,
            note=payload.note,
            rating=payload.rating,
        )

        self.set_status(201)
        self.write(
            UserFeedbackResponse(
                id=feedback.id,
                note=feedback.note,
                rating=feedback.rating,
                comments=[],
                notations=NotationSummary(),
            ).model_dump(mode="json")
        )


class ProductManagerFeedbackHandler(FeedbackHandler):
    async def get(self, *args: str, **kwargs: str) -> None:
        status_param = self.get_query_argument("status", default=None)
        status_filter: FeedbackStatus | None = None
        if status_param:
            try:
                status_filter = FeedbackStatus(status_param)
            except ValueError as error:
                raise HTTPError(
                    422, reason=f"Invalid status filter: {status_param}"
                ) from error

        feedback_entries = await FeedbackService(self.session_factory).list_feedback(
            status=status_filter
        )
        response = [
            ProductManagerFeedbackResponse.from_model(entry).model_dump(mode="json")
            for entry in feedback_entries
        ]
        self.write(json.dumps(response))


class ProductManagerFeedbackDetailHandler(JsonHandler):
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        database_engine: AsyncEngine = self.settings["database_engine"]
        return async_sessionmaker(database_engine, expire_on_commit=False)

    async def patch(self, feedback_id: str) -> None:  # ty: ignore[invalid-method-override]
        try:
            payload: FeedbackManagerUpdate = FeedbackManagerUpdate.model_validate(
                json.loads(self.request.body)
            )
        except (json.JSONDecodeError, ValidationError) as error:
            raise HTTPError(
                422, reason=f"Invalid feedback update payload: {error}"
            ) from error

        try:
            feedback = await FeedbackService(self.session_factory).update_feedback(
                feedback_id=int(feedback_id),
                status=payload.status,
                category=payload.category,
            )
        except FeedbackNotFoundError as error:
            raise HTTPError(404, reason="Feedback not found") from error

        self.write(
            ProductManagerFeedbackResponse.from_model(feedback).model_dump(mode="json")
        )


class DisplayHandler(RequestHandler):
    def get(self, user_id: str) -> None:  # ty: ignore[invalid-method-override]
        self.redirect(f"/web_resources/index.html?user_id={quote(user_id, safe='')}")
