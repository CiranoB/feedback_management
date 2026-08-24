import asyncio

import tornado
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from tornado.web import Application

from api.config.global_settings import settings
from api.database import create_database_engine


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
    return tornado.web.Application(
        handlers=[
            (r"/", MainHandler),
            (r"/post", PostHandler),
            (r"/health/db", DatabaseHealthHandler),
        ],
        database_engine=database_engine,
        debug=settings.debug,
        autoreload=settings.debug,
    )


async def main():
    database_engine = create_database_engine(settings.database_url)
    app: Application = make_app(database_engine)
    app.listen(port=settings.port)

    try:
        await asyncio.Event().wait()
    finally:
        await database_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
