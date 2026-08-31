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
                            "description": "Returns all feedback entries, newest first, with their comments and notation counts.",
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
                            "description": "Submits a new feedback entry with a rating and an optional note.",
                            "tags": ["User feedback"],
                            "security": [{"ApiKeyAuth": []}],
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
                            "description": "Returns all feedback entries with management fields (author, status, category), optionally filtered by status.",
                            "tags": ["Product manager"],
                            "parameters": [
                                {
                                    "name": "status",
                                    "in": "query",
                                    "required": False,
                                    "description": "Filter feedback entries by status",
                                    "schema": {
                                        "type": "string",
                                        "enum": [
                                            "open",
                                            "closed_backlog",
                                            "closed_solved",
                                            "closed_rejected",
                                        ],
                                    },
                                }
                            ],
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
                                },
                                "422": {"description": "Invalid status filter"},
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
                            "summary": "Update feedback status and/or category",
                            "description": "Updates the status and/or category of a single feedback entry.",
                            "tags": ["Product manager"],
                            "security": [{"ApiKeyAuth": []}],
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/FeedbackManagerUpdate"
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
                                "422": {"description": "Invalid update payload"},
                            },
                        },
                    },
                    "/api/product-manager/feedback/{feedback_id}/merge": {
                        "parameters": [
                            {
                                "name": "feedback_id",
                                "in": "path",
                                "required": True,
                                "description": "Source feedback to merge and delete.",
                                "schema": {"type": "integer", "minimum": 1},
                            }
                        ],
                        "post": {
                            "summary": "Merge feedback into another feedback entry",
                            "description": "Moves the source feedback's note and comments into the target feedback, then deletes the source.",
                            "tags": ["Product manager"],
                            "security": [{"ApiKeyAuth": []}],
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/FeedbackMergeRequest"
                                        }
                                    }
                                },
                            },
                            "responses": {
                                "200": {
                                    "description": "The target feedback after merging",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/ProductManagerFeedback"
                                            }
                                        }
                                    },
                                },
                                "404": {
                                    "description": "Source or target feedback not found"
                                },
                                "422": {"description": "Invalid merge payload"},
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
                            "description": "Returns all comments attached to a feedback entry.",
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
                            "description": "Creates a new comment on an existing feedback entry.",
                            "tags": ["User feedback"],
                            "security": [{"ApiKeyAuth": []}],
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
                            "description": "Registers a user's upvote, downvote, or neutral notation on a feedback entry.",
                            "tags": ["User feedback"],
                            "security": [{"ApiKeyAuth": []}],
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
                            "description": "Registers a user's upvote, downvote, or neutral notation on a comment.",
                            "tags": ["User feedback"],
                            "security": [{"ApiKeyAuth": []}],
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
                    "securitySchemes": {
                        "ApiKeyAuth": {
                            "type": "apiKey",
                            "in": "header",
                            "name": "X-API-Key",
                        }
                    },
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
                                    "required": ["author_id", "status", "category"],
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
                                        "category": {
                                            "type": ["string", "null"],
                                            "description": "Null means the feedback has not been categorized yet.",
                                            "enum": [
                                                "frontend",
                                                "backend",
                                                "performance_issues",
                                                "bugs",
                                                None,
                                            ],
                                        },
                                    },
                                },
                            ]
                        },
                        "FeedbackManagerUpdate": {
                            "type": "object",
                            "description": "At least one of status or category must be provided.",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": [
                                        "open",
                                        "closed_backlog",
                                        "closed_solved",
                                        "closed_rejected",
                                    ],
                                },
                                "category": {
                                    "type": "string",
                                    "enum": [
                                        "frontend",
                                        "backend",
                                        "performance_issues",
                                        "bugs",
                                    ],
                                },
                            },
                        },
                        "FeedbackMergeRequest": {
                            "type": "object",
                            "required": ["target_feedback_id"],
                            "properties": {
                                "target_feedback_id": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "description": "Feedback that will absorb the note and comments of the feedback in the path.",
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
                    },
                },
            }
        )
