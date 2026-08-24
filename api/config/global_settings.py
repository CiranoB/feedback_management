from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	port: int = 8888


settings = Settings()
