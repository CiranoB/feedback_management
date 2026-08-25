# feedback_management

Tornado API for collecting rated feedback, backed by PostgreSQL.

## Stakeholder demo: full Compose stack

From the repository root, start both the API and PostgreSQL:

```sh
docker compose --file infra/docker-compose.yml up --build --wait
```

Call the database health check:

```sh
curl http://localhost:8888/health/db
```

It returns `{"database":"available"}` when PostgreSQL accepts a query. Stop the stack with:

```sh
docker compose --file infra/docker-compose.yml down
```

Add `--volumes` to the `down` command to remove the local PostgreSQL data volume.

## Local development: database container only

Start only PostgreSQL:

```sh
docker compose --file infra/docker-compose.yml up postgres
```

In another terminal, run the API locally:

```sh
uv run python main.py
```

The default settings connect to `localhost:5432` using database `feedback_management` and user/password `feedback`. Override any setting with the matching environment variable, for example:

```sh
POSTGRES_HOST=localhost POSTGRES_PORT=5433 uv run python main.py
```

## API and UI

When the API is running, open `http://localhost:8888/docs` for locally served Swagger UI. It documents and lets you execute these endpoints:

- `POST /api/feedback` creates feedback with a required `author_id`, a `rating` from 1 through 5, and an optional `note`.
- `GET /api/feedback` lists feedback, newest first, including each feedback item's
	notations and comments; each comment includes its own notations.
- `GET` and `POST /api/feedback/{feedback_id}/comments` list and add feedback comments.
- `POST /api/feedback/{feedback_id}/notations` adds a notation to feedback.
- `POST /api/comments/{comment_id}/notations` adds a notation to a comment.

Feedback and comments record an `author_id`. A notation stores the submitting `user_id`, a value of `-1`, `0`, or `+1`, and targets exactly one feedback entry or comment. The database allows one notation from a user for each target; authentication can replace these plain identifier fields later.

For a simple browser view of submitted entries, open `http://localhost:8888/display`.

At startup, the application runs `alembic upgrade head`. A new database is initialized with the latest schema and an existing database is upgraded only for pending migrations. Databases created by the earlier application startup path are recognized and stamped at the initial revision, without recreating their existing tables.