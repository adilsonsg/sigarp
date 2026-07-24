from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.price_registry import PriceRegistryRecord
from app.sync.pncp_price_registry_sync import PNCPPriceRegistrySyncService


class FakePNCPClient:
    async def buscar_atas_por_vigencia(self, **_kwargs: Any) -> dict[str, Any]:
        return {
            "data": [
                {
                    "numeroControlePNCPAta": ("33004540000100-1-000001/2025-000001"),
                    "numeroControlePNCPCompra": "33004540000100-1-000001/2025",
                    "numeroAtaRegistroPreco": "12/2025",
                    "anoAta": 2025,
                    "vigenciaInicio": "2025-09-01",
                    "vigenciaFim": "2026-08-31",
                    "cancelado": False,
                    "objetoContratacao": "Registro de preços para projetores",
                    "cnpjOrgao": "33004540000100",
                    "nomeOrgao": "Universidade Federal de Mato Grosso",
                    "possibilidadeAdesao": True,
                }
            ],
            "totalRegistros": 1,
            "totalPaginas": 1,
            "numeroPagina": 1,
            "paginasRestantes": 0,
        }

    async def buscar_orgao(self, _cnpj: str) -> dict[str, Any]:
        return {
            "cnpj": "33004540000100",
            "razaoSocial": "Universidade Federal de Mato Grosso",
            "poderId": "E",
            "esferaId": "F",
        }

    async def close(self) -> None:
        return None


def test_syncs_federal_registry_valid_from_2025(
    db_session: Session,
) -> None:
    service = PNCPPriceRegistrySyncService(
        db_session,
        client=FakePNCPClient(),  # type: ignore[arg-type]
        page_delay_seconds=0,
    )

    stats = __import__("asyncio").run(
        service.synchronize(
            data_inicial=date(2026, 7, 24),
            data_final=date(2026, 7, 24),
            esfera="federal",
        )
    )

    record = db_session.query(PriceRegistryRecord).one()
    assert stats.inseridas == 1
    assert stats.erros == 0
    assert record.numero_ata == "12/2025"
    assert record.situacao == "vigente"
    assert record.orgao_gerenciador.esfera == "federal"
