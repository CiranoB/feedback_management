# feedback_management

Tornado API for collecting rated feedback, backed by PostgreSQL.

From the repository root, start both the API and PostgreSQL:

```sh
docker compose --file infra/docker-compose.yml up --build --wait
```

## Swagger 

Available on `http://localhost:8888/docs`.