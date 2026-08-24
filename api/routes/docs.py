from tornado.web import RequestHandler


class OpenApiHandler(RequestHandler):
    def get(self, *args: str, **kwargs: str) -> None:
        self.write(
            {
                "openapi": "3.1.0",
                "info": {"title": "Feedback Management API", "version": "0.1.0"},
                "paths": {
                    "/api/feedback": {
                        "get": {
                            "summary": "List feedback",
                            "responses": {"200": {"description": "Feedback entries"}},
                        },
                        "post": {
                            "summary": "Create feedback",
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "required": ["rating"],
                                            "properties": {
                                                "note": {"type": ["string", "null"]},
                                                "rating": {
                                                    "type": "integer",
                                                    "minimum": 1,
                                                    "maximum": 5,
                                                },
                                            },
                                        }
                                    }
                                },
                            },
                            "responses": {"201": {"description": "Created"}},
                        },
                    }
                },
            }
        )


class SwaggerUiHandler(RequestHandler):
    def get(self, *args: str, **kwargs: str) -> None:
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.write(
            "<!doctype html><html><head><title>Feedback API docs</title>"
            '<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">'
            '</head><body><div id="swagger-ui"></div>'
            '<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>'
            "<script>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui'})</script>"
            "</body></html>"
        )
