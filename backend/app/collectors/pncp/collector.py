from collections.abc import Mapping
from typing import Any

from app.collectors.base import BaseCollector
from app.collectors.pncp.client import PNCPClient


class PNCPCollector(BaseCollector):
    """Collector facade for PNCP endpoints."""

    name = "pncp"

    def __init__(self, client: PNCPClient | None = None) -> None:
        self._client = client or PNCPClient()
        self._owns_client = client is None

    async def collect(
        self,
        *,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        try:
            return await self._client.get(endpoint, params=params)
        finally:
            if self._owns_client:
                await self._client.close()
