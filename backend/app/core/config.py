from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic Settings reads from environment variables and optional .env file.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_name: str = "BiblioHook Backend"
    environment: str = "dev"
    log_level: str = "INFO"

    # API
    api_v1_prefix: str = "/v1"

    # DB
    database_url: str

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"


@lru_cache
def get_settings() -> Settings:
    # Cached so it’s created once per process.
    return Settings()
