from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.security.models import AuthPrincipalConfig


class Settings(BaseSettings):
    app_name: str = "SIGARP"
    app_version: str = "0.8.0-alpha1"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    pncp_base_url: str = "https://pncp.gov.br/api/consulta"
    pncp_timeout_seconds: float = 30.0
    pncp_max_retries: int = 7
    pncp_backoff_seconds: float = 5.0
    pncp_user_agent: str = "SIGARP/0.8.0-alpha1 (IFMT)"
    pncp_document_max_bytes: int = 50_000_000
    pncp_document_max_text_chars: int = 2_000_000
    pncp_document_max_pages: int = 1000
    auth_principals: list[AuthPrincipalConfig] = Field(default_factory=list)
    database_url: str = "postgresql+psycopg2://sigarp@postgres:5432/sigarp"

    @field_validator("auth_principals")
    @classmethod
    def validate_unique_principals(
        cls, principals: list[AuthPrincipalConfig]
    ) -> list[AuthPrincipalConfig]:
        subjects = [principal.subject for principal in principals]
        hashes = [principal.token_sha256 for principal in principals]
        if len(subjects) != len(set(subjects)):
            raise ValueError("AUTH_PRINCIPALS contém subject duplicado")
        if len(hashes) != len(set(hashes)):
            raise ValueError("AUTH_PRINCIPALS contém token_sha256 duplicado")
        return principals

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
