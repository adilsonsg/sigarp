from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.price_registry import (
    PriceRegistryItemInput,
    PriceRegistryRecordInput,
    SupplierInput,
)


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
            itens=[
                PriceRegistryItemInput(
                    numero_item=1,
                    descricao="Projetor multimídia de curta distância",
                    quantidade_registrada=Decimal("50"),
                    quantidade_empenhada=Decimal("10"),
                    saldo_estimado=Decimal("40"),
                    limite_adesao=Decimal("25"),
                    valor_unitario=Decimal("6500"),
                    fornecedor=SupplierInput(
                        cnpj="12345678000199",
                        razao_social="Fornecedor de Tecnologia Ltda",
                    ),
                )
            ],
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


def test_filters_registry_by_requested_quantity(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_registry(db_session)

    response = client.get(
        "/api/v1/atas",
        params={
            "termo": "projetor",
            "quantidade_minima": "20",
            "vigente_em": "2026-07-24",
            "esfera": "federal",
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    item = response.json()["items"][0]["itens"][0]
    assert Decimal(item["quantidade_registrada"]) == Decimal("50")
    assert Decimal(item["saldo_estimado"]) == Decimal("40")
    assert Decimal(item["limite_adesao"]) == Decimal("25")
    assert item["disponibilidade"] == "ATENDE"

    unavailable = client.get(
        "/api/v1/atas",
        params={
            "termo": "projetor",
            "quantidade_minima": "60",
            "vigente_em": "2026-07-24",
            "esfera": "federal",
        },
    )
    assert unavailable.status_code == 200
    assert unavailable.json()["total"] == 0


def test_excludes_expired_registry(client: TestClient, db_session: Session) -> None:
    seed_registry(db_session)

    response = client.get(
        "/api/v1/atas",
        params={"vigente_em": "2027-01-01", "esfera": "federal"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0
