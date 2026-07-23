from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.services.pncp_opportunity_service import PNCPOpportunityService


def organization_payload(index: int) -> dict[str, str]:
    return {
        "nome": f"Órgão de teste {index}",
        "sigla": f"OT{index}",
        "cnpj": f"10.784.782/000{index}-5{index}",
        "esfera": "federal",
        "uf": "MT",
        "municipio": "Cuiabá",
    }


def test_v1_organizations_use_page_metadata(client: TestClient) -> None:
    for index in range(1, 4):
        response = client.post("/api/v1/orgaos", json=organization_payload(index))
        assert response.status_code == 201

    first_page = client.get("/api/v1/orgaos?page=1&page_size=2")
    second_page = client.get("/api/v1/orgaos?page=2&page_size=2")

    assert first_page.status_code == 200
    assert first_page.json()["page"] == 1
    assert first_page.json()["page_size"] == 2
    assert first_page.json()["total"] == 3
    assert first_page.json()["total_pages"] == 2
    assert len(first_page.json()["items"]) == 2
    assert len(second_page.json()["items"]) == 1


def test_v1_opportunities_runs_and_history_use_page_metadata(
    client: TestClient,
    db_session: Session,
) -> None:
    for index in range(1, 4):
        db_session.add(
            PNCPContractingRecord(
                numero_controle_pncp=f"00000000000000-1-00000{index}/2026",
                objeto_compra=f"Aquisição de projetor {index}",
                uf="MT",
            )
        )
    db_session.commit()
    stats = PNCPOpportunityService(db_session).classify_all()

    opportunities = client.get("/api/v1/pncp/oportunidades?page=1&page_size=2")
    runs = client.get("/api/v1/pncp/oportunidades/execucoes?page=1&page_size=1")
    assessment_id = opportunities.json()["items"][0]["assessment_id"]
    history = client.get(
        f"/api/v1/pncp/oportunidades/{assessment_id}/historico" "?page=1&page_size=1"
    )

    assert opportunities.status_code == 200
    assert opportunities.json()["total"] == 3
    assert opportunities.json()["total_pages"] == 2
    assert len(opportunities.json()["items"]) == 2

    assert runs.status_code == 200
    assert runs.json()["total"] == 1
    assert runs.json()["items"][0]["id"] == stats.execucao_id

    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["assessment_id"] == assessment_id


def test_legacy_list_contract_remains_available(client: TestClient) -> None:
    response = client.get("/orgaos")

    assert response.status_code == 200
    assert response.json() == []
