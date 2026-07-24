from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.price_registry import PriceRegistryRecordInput


def seed_registry(db_session: Session) -> None:
    organization = Organization(
        nome="Universidade Federal de Mato Grosso",
        cnpj="33004540000100",
        esfera="federal",
        uf="MT",
        municipio="Cuiabá",
    )
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)
    PriceRegistryRepository(db_session).upsert(
        PriceRegistryRecordInput(
            numero_controle_pncp="33004540000100-1-000001/2025-000001",
            numero_ata="12/2025",
            numero_processo="33004540000100-1-000001/2025",
            objeto="Registro de preços para projetores de curta distância",
            vigencia_inicio=date(2025, 9, 1),
            vigencia_fim=date(2026, 8, 31),
            situacao="vigente",
            orgao_gerenciador_id=organization.id,
            dados_fonte={"possibilidadeAdesao": True},
        )
    )


def test_lists_2025_registry_still_valid_in_2026(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_registry(db_session)

    response = client.get(
        "/api/v1/atas",
        params={
            "termo": "projetores",
            "vigente_em": "2026-07-24",
            "esfera": "federal",
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["numero_ata"] == "12/2025"
    assert response.json()["items"][0]["vigencia_fim"] == "2026-08-31"
    assert response.json()["items"][0]["orgao"]["esfera"] == "federal"
    assert response.json()["items"][0]["possibilidade_adesao"] is True


def test_excludes_expired_registry(client: TestClient, db_session: Session) -> None:
    seed_registry(db_session)

    response = client.get(
        "/api/v1/atas",
        params={"vigente_em": "2027-01-01", "esfera": "federal"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0
