from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.price_registry import PriceRegistryRecordInput
from app.sync.comprasgov_price_registry_item_sync import (
    ComprasGovPriceRegistryItemSyncService,
)


class FakeItemClient:
    async def buscar_itens_ata(self, numero_controle_pncp_ata: str):
        return {
            "resultado": [
                {
                    "numeroControlePncpAta": numero_controle_pncp_ata,
                    "numeroItem": "00001",
                    "descricaoItem": "Notebook corporativo",
                    "quantidadeHomologadaVencedor": 50,
                    "quantidadeEmpenhada": 12,
                    "maximoAdesao": 30,
                    "valorUnitario": 5000,
                    "niFornecedor": "12345678000199",
                    "nomeRazaoSocialFornecedor": "Tecnologia Ltda",
                    "classificacaoFornecedor": "001",
                    "itemExcluido": False,
                }
            ]
        }


@pytest.mark.asyncio
async def test_synchronizes_federal_registry_items(db_session: Session) -> None:
    organization = Organization(
        nome="Universidade Federal",
        cnpj="33004540000100",
        esfera="federal",
    )
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)
    repository = PriceRegistryRepository(db_session)
    repository.upsert(
        PriceRegistryRecordInput(
            numero_controle_pncp="33004540000100-1-000001/2025-000001",
            numero_ata="12/2025",
            objeto="Aquisição de notebooks",
            vigencia_inicio=date(2025, 9, 1),
            vigencia_fim=date(2026, 8, 31),
            situacao="vigente",
            orgao_gerenciador_id=organization.id,
        )
    )

    service = ComprasGovPriceRegistryItemSyncService(
        db_session,
        client=FakeItemClient(),  # type: ignore[arg-type]
        request_delay_seconds=0,
    )
    stats = await service.synchronize()

    assert stats.atas_processadas == 1
    assert stats.itens_armazenados == 1
    record = repository.get_by_control_number("33004540000100-1-000001/2025-000001")
    assert record is not None
    assert record.itens[0].quantidade_registrada == 50
    assert record.itens[0].quantidade_empenhada == 12
    assert record.itens[0].saldo_estimado == 38
    assert record.itens[0].limite_adesao == 30
