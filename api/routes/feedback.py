from __future__ import annotations

import json
from collections.abc import Sequence
from html import escape

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from tornado.web import HTTPError, RequestHandler

from api.models.feedback import Feedback, FeedbackStatus
from api.models.notation import Notation
from api.services.feedback import FeedbackService


class FeedbackCreate(BaseModel):
    author_id: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=10_000)
    rating: int = Field(ge=1, le=5)


class NotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    value: int
    feedback_id: int | None
    comment_id: int | None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: str
    content: str
    feedback_id: int
    notations: list[NotationResponse]


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: str
    note: str | None
    rating: int
    status: FeedbackStatus
    comments: list[CommentResponse]
    notations: list[NotationResponse]


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
        self.write(
            FeedbackResponse(
                id=feedback.id,
                author_id=feedback.author_id,
                note=feedback.note,
                rating=feedback.rating,
                status=feedback.status,
                comments=[],
                notations=[],
            ).model_dump(mode="json")
        )


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
                '<article><header><span class="feedback-id">#{id}</span>'
                '<span class="status {status_class}">{status}</span></header>'
                '<p class="note">{note}</p><div class="signals">'
                '<div class="rating"><span>Rating</span><meter min="1" max="5" '
                'value="{rating}">{rating}/5</meter><strong>{rating}/5</strong></div>'
                '<div class="community-signal"><span>Community signal</span>'
                '{notations}</div></div><details class="discussion"><summary>'
                "<span>Discussion</span><span>{comment_count} comments</span></summary>"
                "{comments}</details></article>".format(
                    id=entry.id,
                    note=escape(entry.note or "No note provided"),
                    rating=entry.rating,
                    status=escape(entry.status.value.replace("_", " ")),
                    status_class=escape(entry.status.value),
                    notations=render_notations(entry.notations),
                    comment_count=len(entry.comments),
                    comments=(
                        '<ul class="comments">{}</ul>'.format(
                            "".join(
                                f'<li><span class="comment-author">'
                                f"{escape(comment.author_id)}</span>"
                                f"<p>{escape(comment.content)}</p>"
                                f"{render_notations(comment.notations)}</li>"
                                for comment in entry.comments
                            )
                        )
                        if entry.comments
                        else '<p class="empty">No comments yet.</p>'
                    ),
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
            "article header,.signals,.discussion summary{display:flex;align-items:center;justify-content:space-between;gap:16px}"
            ".feedback-id{font-size:22px;font-weight:bold;color:#154c54}.status{border-radius:999px;padding:4px 9px;"
            "background:#d8eadc;color:#1e5b34;text-transform:capitalize;font:700 13px Georgia,serif}"
            ".status.closed_rejected{background:#f3d7d1;color:#8b2b1c}.status.closed_backlog{background:#e7dfb9;color:#675b0d}"
            ".status.closed_solved{background:#d4e7e8;color:#16555b}.note{font-size:18px;line-height:1.45;margin:16px 0}"
            ".signals{border-top:1px solid #d7d1c2;border-bottom:1px solid #d7d1c2;padding:12px 0}"
            ".rating,.community-signal{display:grid;gap:5px;font-size:13px;color:#58636c}.rating{grid-template-columns:auto 110px auto;align-items:center}"
            "meter{width:110px;accent-color:#d07631}.rating strong,.vote-summary strong{color:#17222d;font-size:16px}"
            ".vote-summary{display:flex;align-items:center;gap:8px}.vote-strip{display:flex;flex-wrap:wrap;gap:4px}"
            ".vote{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;color:#fff;font:700 12px Georgia,serif}"
            ".vote.positive{background:#317d4c}.vote.negative{background:#b44a3c}.vote.neutral{background:#6b7780}"
            ".vote-summary.positive strong{color:#317d4c}.vote-summary.negative strong{color:#b44a3c}.vote-empty,.empty{color:#58636c}"
            ".discussion{margin-top:16px}.discussion summary{cursor:pointer;color:#154c54;font-weight:bold;list-style:none}"
            ".discussion summary::-webkit-details-marker{display:none}.discussion summary::after{content:'+';font-size:20px}"
            ".discussion[open] summary::after{content:'-'} .comments{list-style:none;margin:14px 0 0;padding:0}"
            ".comments>li{border-top:1px solid #e4dfd3;padding:12px 0;display:grid;gap:7px}"
            ".comment-author{font-weight:bold}.comments p{line-height:1.4;margin:0}@media(max-width:560px){main{padding:28px 16px}"
            "h1{font-size:32px}.signals{align-items:start;flex-direction:column}.rating{grid-template-columns:auto 1fr auto}}"
            "</style></head><body><main><h1>Community Feedback</h1>"
            f"{cards}</main></body></html>"
        )
