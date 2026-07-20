from datetime import date
from typing import Any

import pytest

from app.collectors.pncp.schemas import PNCPSearchRequest
from app.collectors.pncp.service import PNCPSearchService


class FakePNCPClient:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    async def get(self, endpoint: str, *, params: dict[str, Any] | None = None) -> Any:
        self.calls.append((endpoint, params))
        return self.payload


@pytest.mark.asyncio
async def test_service_builds_official_params_and_filters_keyword() -> None:
    client = FakePNCPClient(
        {
            "data": [
                {"objetoCompra": "Projetor laser Full HD", "srp": True},
                {"objetoCompra": "Notebook", "srp": True},
            ],
            "totalRegistros": 20,
            "totalPaginas": 2,
            "numeroPagina": 1,
            "paginasRestantes": 1,
            "empty": False,
        }
    )
    service = PNCPSearchService(client=client)  # type: ignore[arg-type]
    request = PNCPSearchRequest(
        palavra_chave="projetor",
        data_inicial=date(2026, 7, 1),
        data_final=date(2026, 7, 20),
        codigo_modalidade_contratacao=6,
        uf="mt",
        pagina=1,
        somente_srp=True,
    )

    result = await service.search_contractings(request)

    assert client.calls[0][1] == {
        "dataInicial": "20260701",
        "dataFinal": "20260720",
        "codigoModalidadeContratacao": 6,
        "pagina": 1,
        "uf": "MT",
    }
    assert result.total_registros_fonte == 20
    assert result.total_itens_retornados == 1
    assert result.itens[0].objeto_compra == "Projetor laser Full HD"
