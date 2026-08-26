from tornado.web import RequestHandler


class OpenApiHandler(RequestHandler):
    def get(self, *args: str, **kwargs: str) -> None:
        self.write(
            {
                "openapi": "3.1.0",
                "info": {"title": "Feedback Management API", "version": "0.1.0"},
                "tags": [
                    {
                        "name": "User feedback",
                        "description": "Community feedback, comments, and notations.",
                    },
                    {
                        "name": "Product manager",
                        "description": "Feedback data for product management.",
                    },
                ],
                "paths": {
                    "/api/feedback": {
                        "get": {
                            "summary": "List feedback",
                            "tags": ["User feedback"],
                            "responses": {
                                "200": {
                                    "description": "Feedback entries, newest first",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/UserFeedback"
                                                },
                                            }
                                        }
                                    },
                                }
                            },
                        },
                        "post": {
                            "summary": "Create feedback",
                            "tags": ["User feedback"],
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
                                                "$ref": "#/components/schemas/UserFeedback"
                                            }
                                        }
                                    },
                                },
                                "422": {"description": "Invalid feedback payload"},
                            },
                        },
                    },
                    "/api/product-manager/feedback": {
                        "get": {
                            "summary": "List feedback for product management",
                            "tags": ["Product manager"],
                            "responses": {
                                "200": {
                                    "description": "Feedback entries with management fields, newest first",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/ProductManagerFeedback"
                                                },
                                            }
                                        }
                                    },
                                }
                            },
                        }
                    },
                    "/api/product-manager/feedback/{feedback_id}": {
                        "parameters": [
                            {
                                "name": "feedback_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer", "minimum": 1},
                            }
                        ],
                        "patch": {
                            "summary": "Update feedback status",
                            "tags": ["Product manager"],
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/FeedbackStatusUpdate"
                                        }
                                    }
                                },
                            },
                            "responses": {
                                "200": {
                                    "description": "Updated feedback",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/ProductManagerFeedback"
                                            }
                                        }
                                    },
                                },
                                "404": {"description": "Feedback not found"},
                                "422": {"description": "Invalid status payload"},
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
                            "tags": ["User feedback"],
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
                            "tags": ["User feedback"],
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
                            "tags": ["User feedback"],
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
                            "tags": ["User feedback"],
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
                        "UserFeedback": {
                            "type": "object",
                            "required": [
                                "id",
                                "note",
                                "rating",
                                "comments",
                                "notations",
                            ],
                            "properties": {
                                "id": {"type": "integer"},
                                "note": {"type": ["string", "null"]},
                                "rating": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 5,
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
                        "ProductManagerFeedback": {
                            "allOf": [
                                {"$ref": "#/components/schemas/UserFeedback"},
                                {
                                    "type": "object",
                                    "required": ["author_id", "status"],
                                    "properties": {
                                        "author_id": {"type": "string"},
                                        "status": {
                                            "type": "string",
                                            "enum": [
                                                "open",
                                                "closed_backlog",
                                                "closed_solved",
                                                "closed_rejected",
                                            ],
                                        },
                                    },
                                },
                            ]
                        },
                        "FeedbackStatusUpdate": {
                            "type": "object",
                            "required": ["status"],
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": [
                                        "open",
                                        "closed_backlog",
                                        "closed_solved",
                                        "closed_rejected",
                                    ],
                                }
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
