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
                            "responses": {
                                "200": {
                                    "description": "Feedback entries, newest first",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Feedback"
                                                },
                                            }
                                        }
                                    },
                                }
                            },
                        },
                        "post": {
                            "summary": "Create feedback",
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "required": ["author_id", "rating"],
                                            "properties": {
                                                "author_id": {
                                                    "type": "string",
                                                    "minLength": 1,
                                                    "maxLength": 255,
                                                },
                                                "note": {
                                                    "type": ["string", "null"],
                                                    "maxLength": 10000,
                                                },
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
                            "responses": {
                                "201": {
                                    "description": "Created feedback",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/Feedback"
                                            }
                                        }
                                    },
                                },
                                "422": {"description": "Invalid feedback payload"},
                            },
                        },
                    },
                    "/api/feedback/{feedback_id}/comments": {
                        "parameters": [
                            {
                                "name": "feedback_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer", "minimum": 1},
                            }
                        ],
                        "get": {
                            "summary": "List feedback comments",
                            "responses": {
                                "200": {
                                    "description": "Comments for the feedback entry",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Comment"
                                                },
                                            }
                                        }
                                    },
                                }
                            },
                        },
                        "post": {
                            "summary": "Add a feedback comment",
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "required": ["author_id", "content"],
                                            "properties": {
                                                "author_id": {
                                                    "type": "string",
                                                    "minLength": 1,
                                                    "maxLength": 255,
                                                },
                                                "content": {
                                                    "type": "string",
                                                    "minLength": 1,
                                                    "maxLength": 10000,
                                                },
                                            },
                                        }
                                    }
                                },
                            },
                            "responses": {
                                "201": {
                                    "description": "Created comment",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/Comment"
                                            }
                                        }
                                    },
                                },
                                "422": {
                                    "description": "Invalid comment payload or feedback"
                                },
                            },
                        },
                    },
                    "/api/feedback/{feedback_id}/notations": {
                        "parameters": [
                            {
                                "name": "feedback_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer", "minimum": 1},
                            }
                        ],
                        "post": {
                            "summary": "Add notation to feedback",
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/NotationCreate"
                                        }
                                    }
                                },
                            },
                            "responses": {
                                "201": {
                                    "description": "Created notation",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/Notation"
                                            }
                                        }
                                    },
                                },
                                "422": {"description": "Invalid or duplicate notation"},
                            },
                        },
                    },
                    "/api/comments/{comment_id}/notations": {
                        "parameters": [
                            {
                                "name": "comment_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer", "minimum": 1},
                            }
                        ],
                        "post": {
                            "summary": "Add notation to a comment",
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/NotationCreate"
                                        }
                                    }
                                },
                            },
                            "responses": {
                                "201": {
                                    "description": "Created notation",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/Notation"
                                            }
                                        }
                                    },
                                },
                                "422": {"description": "Invalid or duplicate notation"},
                            },
                        },
                    },
                },
                "components": {
                    "schemas": {
                        "Feedback": {
                            "type": "object",
                            "required": [
                                "id",
                                "author_id",
                                "note",
                                "rating",
                                "status",
                                "comments",
                                "notations",
                            ],
                            "properties": {
                                "id": {"type": "integer"},
                                "author_id": {"type": "string"},
                                "note": {"type": ["string", "null"]},
                                "rating": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 5,
                                },
                                "status": {
                                    "type": "string",
                                    "enum": [
                                        "open",
                                        "closed_backlog",
                                        "closed_solved",
                                        "closed_rejected",
                                    ],
                                },
                                "comments": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/FeedbackComment"
                                    },
                                },
                                "notations": {
                                    "$ref": "#/components/schemas/NotationSummary"
                                },
                            },
                        },
                        "Comment": {
                            "type": "object",
                            "required": ["id", "author_id", "content", "feedback_id"],
                            "properties": {
                                "id": {"type": "integer"},
                                "author_id": {"type": "string"},
                                "content": {"type": "string"},
                                "feedback_id": {"type": "integer"},
                            },
                        },
                        "FeedbackComment": {
                            "allOf": [
                                {"$ref": "#/components/schemas/Comment"},
                                {
                                    "type": "object",
                                    "required": ["notations"],
                                    "properties": {
                                        "notations": {
                                            "$ref": "#/components/schemas/NotationSummary"
                                        }
                                    },
                                },
                            ]
                        },
                        "NotationCreate": {
                            "type": "object",
                            "required": ["user_id", "value"],
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 255,
                                },
                                "value": {
                                    "type": "integer",
                                    "minimum": -1,
                                    "maximum": 1,
                                },
                            },
                        },
                        "Notation": {
                            "type": "object",
                            "required": [
                                "id",
                                "user_id",
                                "value",
                                "feedback_id",
                                "comment_id",
                            ],
                            "properties": {
                                "id": {"type": "integer"},
                                "user_id": {"type": "string"},
                                "value": {
                                    "type": "integer",
                                    "minimum": -1,
                                    "maximum": 1,
                                },
                                "feedback_id": {"type": ["integer", "null"]},
                                "comment_id": {"type": ["integer", "null"]},
                            },
                        },
                        "NotationSummary": {
                            "type": "object",
                            "description": "Counts of notations by value; individual notation details are omitted.",
                            "required": ["positive", "neutral", "negative"],
                            "properties": {
                                "positive": {"type": "integer", "minimum": 0},
                                "neutral": {"type": "integer", "minimum": 0},
                                "negative": {"type": "integer", "minimum": 0},
                            },
                        },
                    }
                },
            }
        )
