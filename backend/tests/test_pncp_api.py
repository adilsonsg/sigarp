from fastapi.testclient import TestClient

from app.api.routes.pncp import get_pncp_search_service
from app.collectors.pncp.schemas import PNCPSearchResponse
from app.main import app


class FakeService:
    async def search_contractings(self, request):
        return PNCPSearchResponse(
            endpoint="/v1/contratacoes/publicacao",
            parametros={"pagina": request.pagina},
            total_registros_fonte=1,
            total_paginas_fonte=1,
            pagina_fonte=1,
            total_itens_retornados=1,
            filtro_local_aplicado=True,
            itens=[{"objetoCompra": "Projetor interativo", "srp": True}],
        )


def test_pncp_search_endpoint(client: TestClient) -> None:
    app.dependency_overrides[get_pncp_search_service] = lambda: FakeService()
    try:
        response = client.post(
            "/pncp/contratacoes/pesquisar",
            json={
                "palavra_chave": "projetor",
                "data_inicial": "2026-07-01",
                "data_final": "2026-07-20",
                "codigo_modalidade_contratacao": 6,
                "uf": "MT",
                "pagina": 1,
                "somente_srp": True,
            },
        )
    finally:
        app.dependency_overrides.pop(get_pncp_search_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total_itens_retornados"] == 1
    assert body["itens"][0]["objeto_compra"] == "Projetor interativo"


def test_pncp_search_validates_date_range(client: TestClient) -> None:
    response = client.post(
        "/pncp/contratacoes/pesquisar",
        json={
            "data_inicial": "2026-07-20",
            "data_final": "2026-07-01",
            "codigo_modalidade_contratacao": 6,
        },
    )

    assert response.status_code == 422


def test_pncp_get_search_endpoint(client: TestClient) -> None:
    app.dependency_overrides[get_pncp_search_service] = lambda: FakeService()
    try:
        response = client.get(
            "/pncp/search",
            params={
                "termo": "projetor",
                "data_inicial": "2026-07-01",
                "data_final": "2026-07-20",
                "codigo_modalidade_contratacao": 6,
                "uf": "mt",
                "pagina": 1,
                "somente_srp": True,
            },
        )
    finally:
        app.dependency_overrides.pop(get_pncp_search_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total_itens_retornados"] == 1
    assert body["itens"][0]["objeto_compra"] == "Projetor interativo"


def test_pncp_get_search_validates_date_range(client: TestClient) -> None:
    response = client.get(
        "/pncp/search",
        params={
            "data_inicial": "2026-07-20",
            "data_final": "2026-07-01",
            "codigo_modalidade_contratacao": 6,
        },
    )

    assert response.status_code == 422
