from __future__ import annotations

import json
from collections.abc import Sequence
from html import escape

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tornado.web import HTTPError, RequestHandler

from api.models.feedback import Feedback, FeedbackStatus
from api.services.feedback import FeedbackService


class FeedbackCreate(BaseModel):
    author_id: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=10_000)
    rating: int = Field(ge=1, le=5)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: str
    note: str | None
    rating: int
    status: FeedbackStatus


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
            FeedbackResponse.model_validate(entry).model_dump(mode="json")
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
        self.write(FeedbackResponse.model_validate(feedback).model_dump(mode="json"))


class DisplayHandler(RequestHandler):
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        database_engine: AsyncEngine = self.settings["database_engine"]
        return async_sessionmaker(database_engine, expire_on_commit=False)

    async def get(self, *args: str, **kwargs: str) -> None:  # ty: ignore[invalid-method-override]
        feedback_entries: Sequence[Feedback] = await FeedbackService(
            self.session_factory
        ).list_feedback()

        cards = (
            "".join(
                "<article><h2>Feedback #{id}</h2><p>{note}</p>"
                "<dl><dt>Rating</dt><dd>{rating}/5</dd><dt>Status</dt>"
                "<dd>{status}</dd></dl></article>".format(
                    id=entry.id,
                    note=escape(entry.note or "No note provided"),
                    rating=entry.rating,
                    status=escape(entry.status.value.replace("_", " ")),
                )
                for entry in feedback_entries
            )
            or '<p class="empty">No feedback has been submitted yet.</p>'
        )
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.write(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>Feedback</title><style>"
            "body{margin:0;background:#f5f3ea;color:#17222d;font:16px Georgia,serif}"
            "main{max-width:800px;margin:0 auto;padding:48px 24px}"
            "h1{font:700 40px/1.1 Georgia,serif;margin:0 0 32px;color:#154c54}"
            "article{background:#fff;border:1px solid #d7d1c2;border-radius:6px;"
            "padding:20px 24px;margin:12px 0;box-shadow:0 2px 8px #17222d12}"
            "h2{font-size:20px;margin:0 0 12px}p{line-height:1.5}"
            "dl{display:grid;grid-template-columns:90px 1fr;gap:6px;margin:16px 0 0}"
            "dt{font-weight:bold}dd{margin:0;text-transform:capitalize}.empty{color:#58636c}"
            "</style></head><body><main><h1>Community Feedback</h1>"
            f"{cards}</main></body></html>"
        )
