# feedback_management

A live version is available at [https://feedback-management-l0qx.onrender.com/docs](https://feedback-management-l0qx.onrender.com/docs).

Tornado API for collecting rated feedback, backed by PostgreSQL.

You can explore it via Swagger, or through the web resources (user and product manager views):

- User view: `/web/{user_id}`
- Product manager view: `/web_resources/product_manager.html?user_id={user_id}`

To interact with the live version, a password is needed. It was sent over email. GET endpoints are open.


## Docker compose version

From the repository root, start both the API and PostgreSQL:

```sh
docker compose --file infra/docker-compose.yml up --build --wait
```

## Swagger 

Available on `http://localhost:8888/docs`.