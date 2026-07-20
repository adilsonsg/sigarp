from collections.abc import Mapping
from datetime import date
from typing import Any

import httpx

from app.clients.base import BaseHttpClient, SleepCallable
from app.collectors.pncp.config import PNCPConfig
from app.collectors.pncp.endpoints import CONTRACTING_BY_PUBLICATION


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
        """Perform a raw GET request against a PNCP endpoint."""
        return await self.get_json(endpoint, params=params)

    async def buscar_contratacoes_publicadas(
        self,
        *,
        data_inicial: date,
        data_final: date,
        codigo_modalidade_contratacao: int,
        pagina: int = 1,
        uf: str | None = None,
    ) -> Any:
        """Fetch contracting notices by publication date from PNCP."""
        params: dict[str, str | int] = {
            "dataInicial": data_inicial.strftime("%Y%m%d"),
            "dataFinal": data_final.strftime("%Y%m%d"),
            "codigoModalidadeContratacao": codigo_modalidade_contratacao,
            "pagina": pagina,
        }
        if uf:
            params["uf"] = uf.strip().upper()

        return await self.get(CONTRACTING_BY_PUBLICATION, params=params)
