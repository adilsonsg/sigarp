from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.price_registry import PriceRegistryRecordInput


def create_organization(db_session: Session) -> Organization:
    organization = Organization(
        nome="Instituto Federal de Mato Grosso",
        sigla="IFMT",
        cnpj="10784782000150",
        esfera="federal",
        uf="MT",
        municipio="Cuiabá",
    )
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)
    return organization


def record_payload(
    organization_id: int,
    description: str = "Projetor laser",
) -> PriceRegistryRecordInput:
    return PriceRegistryRecordInput(
        numero_controle_pncp="10784782000150-1-000001/2026",
        numero_ata="15/2026",
        numero_processo="23188.000001/2026-00",
        objeto="Registro de preços para equipamentos audiovisuais",
        vigencia_inicio=date(2026, 7, 1),
        vigencia_fim=date(2027, 6, 30),
        situacao="Vigente",
        orgao_gerenciador_id=organization_id,
        url_pncp="https://pncp.gov.br/app/atas/10784782000150/2026/1",
        itens=[
            {
                "numero_item": 1,
                "descricao": description,
                "fabricante": "Epson",
                "marca": "Epson",
                "modelo": "BrightLink 760Wi",
                "unidade_medida": "unidade",
                "quantidade_registrada": Decimal("20"),
                "valor_unitario": Decimal("21000.00"),
                "fornecedor": {
                    "cnpj": "12345678000199",
                    "razao_social": "Fornecedor de Teste Ltda",
                },
            }
        ],
    )


def test_upsert_creates_record_items_and_supplier(db_session: Session) -> None:
    organization = create_organization(db_session)
    repository = PriceRegistryRepository(db_session)

    record = repository.upsert(record_payload(organization.id))

    assert record.id > 0
    assert record.numero_ata == "15/2026"
    assert len(record.itens) == 1
    assert record.itens[0].modelo == "BrightLink 760Wi"
    assert record.itens[0].fornecedor is not None
    assert record.itens[0].fornecedor.cnpj == "12345678000199"


def test_upsert_updates_record_without_duplication(db_session: Session) -> None:
    organization = create_organization(db_session)
    repository = PriceRegistryRepository(db_session)
    repository.upsert(record_payload(organization.id))

    updated = repository.upsert(
        record_payload(organization.id, description="Projetor interativo Full HD")
    )

    assert len(updated.itens) == 1
    assert updated.itens[0].descricao == "Projetor interativo Full HD"


def test_search_matches_model_and_can_limit_active_records(db_session: Session) -> None:
    organization = create_organization(db_session)
    repository = PriceRegistryRepository(db_session)
    repository.upsert(record_payload(organization.id))

    result = repository.search(term="BrightLink 760Wi", only_active=True)

    assert len(result) == 1
    assert result[0].numero_ata == "15/2026"
