# feedback_management

Tornado API with an asynchronous PostgreSQL health check at `GET /health/db`.

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