import asyncio

import tornado
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from swagger_ui import api_doc
from tornado.web import Application

from api.config.global_settings import settings
from api.database import create_database_engine, upgrade_database
from api.models.comments import Comments  # noqa: F401
from api.models.notation import Notation  # noqa: F401
from api.routes.comments import (
    CommentNotationHandler,
    CommentsHandler,
    FeedbackNotationHandler,
)
from api.routes.docs import OpenApiHandler
from api.routes.feedback import DisplayHandler, FeedbackHandler


class MainHandler(tornado.web.RequestHandler):
    def get(self) -> None:  # ty: ignore[invalid-method-override]
        self.write(chunk="Hello, world")


class PostHandler(tornado.web.RequestHandler):
    def get(self) -> None:  # ty: ignore[invalid-method-override]
        self.write("<h1> This is Post 1 </h1>")


class DatabaseHealthHandler(tornado.web.RequestHandler):
    async def get(self) -> None:  # ty: ignore[invalid-method-override]
        database_engine: AsyncEngine = self.settings["database_engine"]

        try:
            async with database_engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            self.set_status(503)
            self.write({"database": "unavailable"})
            return

        self.write({"database": "available"})


def make_app(database_engine: AsyncEngine) -> tornado.web.Application:
    app = tornado.web.Application(
        handlers=[
            (r"/", MainHandler),
            (r"/post", PostHandler),
            (r"/health/db", DatabaseHealthHandler),
            (r"/api/feedback", FeedbackHandler),
            (r"/api/feedback/([0-9]+)/comments", CommentsHandler),
            (r"/api/feedback/([0-9]+)/notations", FeedbackNotationHandler),
            (r"/api/comments/([0-9]+)/notations", CommentNotationHandler),
            (r"/display", DisplayHandler),
            (r"/openapi.json", OpenApiHandler),
            (r"/docs/openapi.json", OpenApiHandler),
        ],
        database_engine=database_engine,
        debug=settings.debug,
        autoreload=settings.debug,
    )
    api_doc(
        app,
        app_type="tornado",
        config_rel_url="/openapi.json",
        url_prefix="/docs",
        title="Feedback API docs",
        host_inject=False,
    )
    return app


async def main():
    database_engine = create_database_engine(settings.database_url)
    await upgrade_database(database_engine)
    app: Application = make_app(database_engine)
    app.listen(port=settings.port)

    try:
        await asyncio.Event().wait()
    finally:
        await database_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
