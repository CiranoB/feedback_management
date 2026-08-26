from __future__ import annotations

import json
from collections.abc import Sequence
from html import escape
from urllib.parse import quote

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tornado.web import HTTPError, RequestHandler

from api.models.comments import Comments
from api.models.feedback import Feedback, FeedbackStatus
from api.models.notation import Notation
from api.services.feedback import FeedbackService


class FeedbackCreate(BaseModel):
    author_id: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=10_000)
    rating: int = Field(ge=1, le=5)


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

    @classmethod
    def from_model(cls, feedback: Feedback) -> ProductManagerFeedbackResponse:
        return cls(
            id=feedback.id,
            author_id=feedback.author_id,
            note=feedback.note,
            rating=feedback.rating,
            status=feedback.status,
            comments=[
                CommentResponse.from_model(comment) for comment in feedback.comments
            ],
            notations=NotationSummary.from_notations(feedback.notations),
        )


class JsonHandler(RequestHandler):
    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "application/json")

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
        feedback_entries = await FeedbackService(self.session_factory).list_feedback()
        response = [
            ProductManagerFeedbackResponse.from_model(entry).model_dump(mode="json")
            for entry in feedback_entries
        ]
        self.write(json.dumps(response))


def render_notations(notations: Sequence[Notation]) -> str:
    if not notations:
        return '<span class="vote-empty">No votes yet</span>'

    score = sum(notation.value for notation in notations)
    score_class = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    votes = "".join(
        f'<span class="vote {"positive" if notation.value > 0 else "negative" if notation.value < 0 else "neutral"}" '
        f'title="{escape(notation.user_id)}: {notation.value:+d}">'
        f"{notation.value:+d}</span>"
        for notation in notations
    )
    return (
        f'<div class="vote-summary {score_class}"><strong>{score:+d}</strong>'
        f'<span class="vote-strip" aria-label="{len(notations)} votes">{votes}</span>'
        "</div>"
    )


class DisplayHandler(RequestHandler):
    def get(self, user_id: str) -> None:  # ty: ignore[invalid-method-override]
        self.redirect(f"/web_resources/index.html?user_id={quote(user_id, safe='')}")
