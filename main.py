import asyncio
import logging
from pathlib import Path

import tornado
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from swagger_ui import api_doc
from tornado.web import Application, StaticFileHandler

from api.config.global_settings import settings
from api.database import create_database_engine, upgrade_database
from api.models.comments import Comments  # noqa: F401
from api.models.notation import Notation  # noqa: F401
from api.routes.comments import CommentsHandler
from api.routes.docs import OpenApiHandler
from api.routes.feedback import (
    DisplayHandler,
    FeedbackHandler,
    ProductManagerFeedbackDetailHandler,
    ProductManagerFeedbackHandler,
    ProductManagerFeedbackMergeHandler,
)
from api.routes.notation import CommentNotationHandler, FeedbackNotationHandler

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )


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
    web_resources_path = Path(__file__).parent / "web_resources"
    app = tornado.web.Application(
        handlers=[
            (r"/health/db", DatabaseHealthHandler),
            (r"/api/feedback", FeedbackHandler),
            (r"/api/product-manager/feedback", ProductManagerFeedbackHandler),
            (
                r"/api/product-manager/feedback/([0-9]+)",
                ProductManagerFeedbackDetailHandler,
            ),
            (
                r"/api/product-manager/feedback/([0-9]+)/merge",
                ProductManagerFeedbackMergeHandler,
            ),
            (r"/api/feedback/([0-9]+)/comments", CommentsHandler),
            (r"/api/feedback/([0-9]+)/notations", FeedbackNotationHandler),
            (r"/api/comments/([0-9]+)/notations", CommentNotationHandler),
            (r"/web/([^/]+)", DisplayHandler),
            (r"/web_resources/(.*)", StaticFileHandler, {"path": web_resources_path}),
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
    configure_logging()
    app: Application = make_app(database_engine)
    app.listen(port=settings.port)
    logger.info("Feedback API listening on port %s", settings.port)

    try:
        await asyncio.Event().wait()
    finally:
        await database_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
