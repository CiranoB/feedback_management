import asyncio

import tornado
from tornado.web import Application

from api.config.global_settings import settings


class MainHandler(tornado.web.RequestHandler):
    def get(self) -> None:  # ty: ignore[invalid-method-override]
        self.write(chunk="Hello, world")


class PostHandler(tornado.web.RequestHandler):
    def get(self) -> None:  # ty: ignore[invalid-method-override]
        self.write("<h1> This is Post 1 </h1>")


def make_app() -> tornado.web.Application:
    return tornado.web.Application(
        handlers=[(r"/", MainHandler), (r"/post", PostHandler)],
        debug=True,
        autoreload=True,
    )


async def main():
    app: Application = make_app()
    app.listen(port=settings.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
