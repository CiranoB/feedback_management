# feedback_management

## Run with Docker

Build the image from the repository root:

```sh
docker build --tag feedback-management .
```

Run the API on the default port:

```sh
docker run --rm --publish 8888:8888 feedback-management
```

Set `PORT` to use a different application port:

```sh
docker run --rm --publish 8080:8080 --env PORT=8080 feedback-management
```