"""Application configuration via pydantic-settings."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # TODO: fill out all config fields
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/k8s_security"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-me"
    enable_mock_data: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
