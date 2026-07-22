from decimal import Decimal

import httpx
import pytest

from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.config import PNCPConfig
from app.sync.pncp_item_sync import PNCPItemSyncService


@pytest.mark.asyncio
async def test_client_builds_contracting_items_endpoint() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=[], request=request)

    config = PNCPConfig(
        base_url="https://pncp.test",
        timeout_seconds=1,
        max_retries=0,
        backoff_seconds=0.01,
        user_agent="SIGARP-Test",
    )
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(config, client=http_client)
        result = await client.buscar_itens_contratacao(
            cnpj="04.264.173/0001-78",
            ano=2026,
            sequencial=54,
            pagina=2,
            tamanho_pagina=50,
        )

    assert captured_request is not None
    assert captured_request.url.host == "pncp.gov.br"
    assert captured_request.url.path == (
        "/api/pncp/v1/orgaos/04264173000178/compras/2026/54/itens"
    )
    assert captured_request.url.query == b""
    assert result["data"] == []
    assert result["totalPaginas"] == 1


def test_extract_items_page_accepts_official_shape() -> None:
    items, total_pages = PNCPItemSyncService._extract_page(
        {
            "data": [{"numeroItem": 1, "descricao": "Projetor"}],
            "totalPaginas": 3,
        }
    )
    assert len(items) == 1
    assert total_pages == 3


def test_normalize_item() -> None:
    result = PNCPItemSyncService._normalize(
        10,
        {
            "numeroItem": 1,
            "descricao": "Projetor multimídia laser",
            "quantidade": 20,
            "valorUnitarioEstimado": 15000.50,
            "unidadeMedida": "Unidade",
        },
    )
    assert result is not None
    assert result.contracting_id == 10
    assert result.quantidade == Decimal("20")
    assert result.valor_unitario_estimado == Decimal("15000.5")
