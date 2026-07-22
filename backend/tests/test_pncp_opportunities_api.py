from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.services.pncp_opportunity_service import PNCPOpportunityService


def test_list_opportunities_endpoint(client: TestClient, db_session: Session) -> None:
    db_session.add(
        PNCPContractingRecord(
            numero_controle_pncp="00000000000000-1-000001/2026",
            objeto_compra="Aquisição de projetor laser",
            uf="MT",
        )
    )
    db_session.commit()
    PNCPOpportunityService(db_session).classify_all()

    response = client.get(
        "/pncp/oportunidades",
        params={
            "classificacao": "CANDIDATA_DOCUMENTO",
            "uf": "MT",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["numero_controle_pncp"] == ("00000000000000-1-000001/2026")
    assert body[0]["perfil_versao"] == "1.0.0"
