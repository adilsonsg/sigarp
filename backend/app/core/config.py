from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SIGARP"
    app_version: str = "0.3.0-alpha1"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    pncp_base_url: str = "https://pncp.gov.br/api/consulta"
    pncp_timeout_seconds: float = 30.0
    pncp_max_retries: int = 4
    pncp_backoff_seconds: float = 1.0
    pncp_user_agent: str = "SIGARP/0.3 (IFMT)"
    database_url: str = "postgresql+psycopg2://sigarp:sigarp123@postgres:5432/sigarp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
