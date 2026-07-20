from dataclasses import dataclass

from app.core.config import Settings, settings


@dataclass(frozen=True, slots=True)
class PNCPConfig:
    base_url: str
    timeout_seconds: float
    max_retries: int
    backoff_seconds: float
    user_agent: str

    @classmethod
    def from_settings(cls, source: Settings = settings) -> "PNCPConfig":
        return cls(
            base_url=source.pncp_base_url.rstrip("/"),
            timeout_seconds=source.pncp_timeout_seconds,
            max_retries=source.pncp_max_retries,
            backoff_seconds=source.pncp_backoff_seconds,
            user_agent=source.pncp_user_agent,
        )
