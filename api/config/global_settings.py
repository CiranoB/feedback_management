from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8888
    debug: bool = True
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "feedback"
    postgres_password: str = "feedback"
    postgres_database: str = "feedback_management"
    auth_token: str = "FeedbackChallenge"

    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        )


settings = Settings()
