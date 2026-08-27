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

## Authentication

Write requests (`POST`/`PATCH`) to `/api/*` must include an `X-API-Key` header matching the `AUTH_TOKEN` environment variable (defaults to `FeedbackChallenge`). Reading data (`GET`) is not authenticated. Override the token with, for example:

```sh
AUTH_TOKEN=my-secret-token uv run python main.py
```

- **Web UI**: enter the token in the "Auth token" box at the top of each page; it is stored in the browser's local storage and sent with every write request.
- **Swagger UI**: click the green **Authorize** button at `http://localhost:8888/docs` and enter the token.

## Swagger 

Available on `http://localhost:8888/docs`.