from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Whagent Backend"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = (
        "postgresql+psycopg://car_agent_user:car_agent_password"
        "@postgres:5432/car_agent_db"
    )

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    internal_api_key: str = "change-me"

    openai_api_key: str = ""
    default_openai_model: str = "gpt-4.1-mini"
    ai_runtime_enabled: bool = True

    evolution_api_base_url: str = ""
    evolution_api_key: str = ""
    webhook_public_base_url: str = "http://localhost:8000"

    crm_mock_base_url: str = "http://crm-mock:8001"

    redis_url: str = "redis://redis:6379/0"
    agent_debounce_seconds: int = 8
    conversation_lock_seconds: int = 60

    debug_allow_from_me_as_inbound: bool = False
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"prod", "production"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
