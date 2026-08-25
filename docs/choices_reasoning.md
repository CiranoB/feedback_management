# Programming Language: Python
Challenge requirement

# Python Version 3.14
At the time that this project was built, this version is a good balance between new features/stability. It is the last "stable" version.
![alt text](images/image.png)

# Package manager: UV
This choice was just because I have more experience with, but I know there are some other projects available for this purpose

# Project Structure: pyproject.toml
Following PEP 621: https://peps.python.org/pep-0621/

# Pre-commit, linting, static typing check, etc
Pre-commit runs Ruff for linting and ty for whole-project static type checking. For this project I'll try a pretty recent type checker written in Rust called ty. This choice don't have a specific reason, but just the curiosity to see how it behaves (and check if can be faster than MyPy, which was really slow in my past experiences)

# Framework
Challenge Requirement

Tornado remains the HTTP framework, so OpenAPI and Swagger UI are served as ordinary Tornado routes at `/openapi.json` and `/docs`. This keeps the interactive API documentation available without introducing a second web framework.

# Database: Postgres
Has widely doc available, it is open-source and free to use

# Feedback model
The `Feedback` SQLAlchemy model contains an identifier, an optional text note, a required rating, and a manager-facing status. A database check constraint limits ratings to the challenge-defined range of 1 (bad) through 5 (very good). Status is an enum that defaults to `open` and supports the three required closed states: backlog, solved, and rejected.

# Comments model
The `Comments` model stores a required `author_id` and text content, and belongs to one `Feedback` record through a required foreign key. The reverse `Feedback.comments` relationship exposes all comments associated with a feedback entry.

# Notation model
`Notation` stores a user's `-1`, `0`, or `+1` assessment of either one feedback entry or one comment. It retains the submitting `user_id` as a simple application field until authentication is introduced. Database constraints require exactly one target and permit each user only one notation per feedback entry and one per comment. Feedback and comments retain `author_id` so the API can subsequently prevent self-notation.

# ORM usage: SQLAlchemy + asyncpg
Since tornado is a framework to overcome C10k problem, a good pair to it is an async connection with the DB.

# Database versioning tool: Alembic
Since I'm decided to use ORM, Alembic will help me to write the db. versions. It also allow me to navigate across db versions due its "upgrade" and "downgrade" methods. 

The application runs `alembic upgrade head` through the existing asynchronous SQLAlchemy engine during startup. This creates a fresh schema from the initial revision and applies only pending revisions to an existing database. The first run also stamps databases that contain the complete pre-migration schema, preserving data created before Alembic was introduced.

# Design pattern: MVC-ish
Since it will be a small API, I will go by simplicity and only write 3 layers (controller, service and repository) - or something similar.

# Service layer
`FeedbackService`, `CommentsService`, and `NotationService` encapsulate asynchronous database operations behind a shared session-factory pattern. Comment operations list and create comments for a feedback entry; notation creation supports exactly one feedback or comment target, with database constraints enforcing target validity and per-user uniqueness.

# Infra
To make the code executable in another machine easily, the project provides a Docker Compose stack with PostgreSQL and the API. The same Compose file also supports local development by starting only the PostgreSQL service; the Tornado process then uses the default connection settings for `localhost`.

# Database health check
`GET /health/db` acquires an asynchronous SQLAlchemy connection and executes `SELECT 1`. It returns HTTP 200 when PostgreSQL is reachable and HTTP 503 when the database query fails.

# Container image
The application image uses two `python:3.14-alpine` stages. The builder stage resolves production dependencies with UV, while the runtime stage only contains the application source and the prepared virtual environment. This keeps dependency tooling out of the final image.

