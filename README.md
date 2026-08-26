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
- `GET /api/feedback` lists the community feedback view, newest first. It includes the
	feedback note, rating, notation counts, and comments with their notation counts; it
	does not expose submitter identifiers or management status.
- `GET /api/product-manager/feedback` lists the product manager feedback view with the
	same community data plus the feedback submitter identifier and management status.
- `PATCH /api/product-manager/feedback/{feedback_id}` changes a ticket's management
	status. Send one of `open`, `closed_backlog`, `closed_solved`, or `closed_rejected`
	in a JSON body such as `{"status":"closed_solved"}`.
- `GET` and `POST /api/feedback/{feedback_id}/comments` list and add feedback comments.
- `POST /api/feedback/{feedback_id}/notations` adds a notation to feedback.
- `POST /api/comments/{comment_id}/notations` adds a notation to a comment.

Feedback and comments record an `author_id`. A notation stores the submitting `user_id`, a value of `-1`, `0`, or `+1`, and targets exactly one feedback entry or comment. The database allows one notation from a user for each target; authentication can replace these plain identifier fields later.

For the interactive browser view, open `http://localhost:8888/web/{user-id}`, replacing
`{user-id}` with the user identifier to submit comments and notations as. For example,
`http://localhost:8888/web/alex` posts Alex's comments and votes. The page lets that user
comment on feedback and give `+1`, `0`, or `-1` notations to feedback and comments.
Use the **Switch user** control on the community page to change the active identifier;
all subsequent feedback, comments, and notations use the newly selected user.
This URL redirects to the static page served from `web_resources/`; its HTML, CSS, and
JavaScript are kept there separately from the API route handlers.

The user page links to the product manager visualization, which shows management status and
submitter information. The product manager can update each ticket's status from its selector.
Feedback merging is intentionally not implemented.

At startup, the application runs `alembic upgrade head`. A new database is initialized with the latest schema and an existing database is upgraded only for pending migrations. Databases created by the earlier application startup path are recognized and stamped at the initial revision, without recreating their existing tables.