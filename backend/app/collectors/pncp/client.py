from collections.abc import Mapping
from typing import Any

import httpx

from app.clients.base import BaseHttpClient, SleepCallable
from app.collectors.pncp.config import PNCPConfig


class PNCPClient(BaseHttpClient):
    """Asynchronous client for the official PNCP Consulta API."""

    def __init__(
        self,
        config: PNCPConfig | None = None,
        *,
        client: httpx.AsyncClient | None = None,
        sleep: SleepCallable | None = None,
    ) -> None:
        self.config = config or PNCPConfig.from_settings()
        kwargs: dict[str, Any] = {
            "service_name": "PNCP",
            "base_url": self.config.base_url,
            "timeout_seconds": self.config.timeout_seconds,
            "max_retries": self.config.max_retries,
            "backoff_seconds": self.config.backoff_seconds,
            "user_agent": self.config.user_agent,
            "client": client,
        }
        if sleep is not None:
            kwargs["sleep"] = sleep
        super().__init__(**kwargs)

    async def get(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        return await self.get_json(endpoint, params=params)
