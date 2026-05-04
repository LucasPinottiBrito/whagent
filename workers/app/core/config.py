from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    backend_internal_api_url: str = "http://backend:8000"
    backend_internal_api_key: str = "change-me"
    redis_url: str = "redis://redis:6379/0"
    conversation_lock_seconds: int = 60
    worker_poll_interval_seconds: int = 1
    worker_batch_size: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
