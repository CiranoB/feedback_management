# Authentication + Authorization process
For demonstration purposes, the application currently relies on a path variable to identify users. This is not production-ready. Before deploying this project, users should be authenticated through a third-party provider, such as Google Sign-In.

# Expose swagger on prod. env.
Swagger documentation should not be available to clients in the production environment. It is currently exposed only because this is not a production-ready application.

# MVC -> Clean Arch
Because the number of features is currently small, a fully reusable, complex design pattern was unnecessary. If the system grows, it would be better to adopt a more robust architecture based on SOLID principles.

# Database Connection Pools
No study has been performed on the database and API capacity under heavy workloads. In a production system, it would be necessary to determine how many simultaneous connections each API instance and database replica can handle.

# Branch strategy, CI/CD
Because I was the only developer, I committed everything directly to `main`. In a team, this should be avoided. I prefer [Gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) or [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow), together with a CI/CD pipeline.

# Load test
If this API is expected to handle heavy workloads, load testing should be performed to assess its behavior under multiple concurrent requests.

# Telemetry
The API lacks telemetry.

# Pagination
As the amount of data grows, pagination will become essential.

# DTO
Since the ammount of data transactioned across the layers (services, router, etc) are minimal, this project does not uses DTOs. But soon as the ammount of data increase, it is particularly important to use it.

# Middleware Errors Handler
In a particular case, the Database can be locked and return error. Right now, we don't have a good handler for this. For prod. env. I'd use something like: https://fastapi.tiangolo.com/tutorial/middleware/