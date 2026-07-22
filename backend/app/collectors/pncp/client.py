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

    async def buscar_itens_contratacao(
        self,
        *,
        cnpj: str,
        ano: int,
        sequencial: int,
        pagina: int = 1,
        tamanho_pagina: int = 100,
    ) -> Any:
        """Fetch all items from the PNCP Integration API.

        Pagination arguments remain in the signature for backward compatibility.
        The integration endpoint returns the complete JSON list.
        """
        del pagina, tamanho_pagina
        cnpj_normalizado = "".join(
            character for character in str(cnpj) if character.isdigit()
        )
        endpoint = (
            "https://pncp.gov.br/api/pncp/v1/orgaos/"
            f"{cnpj_normalizado}/compras/{ano}/{sequencial}/itens"
        )
        payload = await self.get(endpoint)

        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = (
                payload.get("data")
                or payload.get("itens")
                or payload.get("content")
                or []
            )
        else:
            items = []

        return {
            "data": items,
            "itens": items,
            "content": items,
            "totalPaginas": 1,
            "numeroPagina": 1,
            "pagina": 1,
            "totalElementos": len(items),
        }

    async def buscar_documentos_contratacao(
        self,
        *,
        cnpj: str,
        ano: int,
        sequencial: int,
    ) -> Any:
        """Fetch contracting document metadata from the Integration API."""
        cnpj_normalizado = "".join(
            character for character in str(cnpj) if character.isdigit()
        )
        endpoint = (
            "https://pncp.gov.br/api/pncp/v1/orgaos/"
            f"{cnpj_normalizado}/compras/{ano}/{sequencial}/arquivos"
        )
        return await self.get(endpoint)

    async def baixar_documento(self, url: str) -> httpx.Response:
        """Download raw contracting document content with centralized retries."""
        return await self.request(
            "GET",
            url,
            headers={
                "Accept": (
                    "application/pdf, application/zip, "
                    "application/octet-stream, text/plain, */*"
                )
            },
        )
