from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.sync.pncp_sync import PNCPSyncService


class FakePNCPClient:
    def __init__(self) -> None:
        self.pages: list[int] = []

    async def buscar_contratacoes_publicadas(self, **kwargs):  # type: ignore[no-untyped-def]
        page = kwargs["pagina"]
        self.pages.append(page)
        data = [
            {
                "numeroControlePNCP": f"00000000000000-1-00000{page}/2026",
                "numeroCompra": str(page),
                "anoCompra": 2026,
                "objetoCompra": f"Aquisição de projetor página {page}",
                "modalidadeId": 6,
                "modalidadeNome": "Pregão - Eletrônico",
                "srp": True,
                "orgaoEntidade": {
                    "cnpj": "12.345.678/0001-99",
                    "razaoSocial": "Órgão Teste",
                },
                "unidadeOrgao": {
                    "nomeUnidade": "Campus",
                    "ufSigla": "mt",
                    "municipioNome": "Cuiabá",
                },
            }
        ]
        return {
            "data": data,
            "totalRegistros": 2,
            "totalPaginas": 2,
            "numeroPagina": page,
            "paginasRestantes": 2 - page,
            "empty": False,
        }

    async def close(self) -> None:
        raise AssertionError("Injected client must not be closed")


@pytest.mark.asyncio
async def test_sync_paginates_and_inserts(db_session: Session) -> None:
    client = FakePNCPClient()
    stats = await PNCPSyncService(
        db_session, client=client, page_delay_seconds=0
    ).synchronize(
        data_inicial=date(2026, 7, 1),
        data_final=date(2026, 7, 20),
        codigo_modalidade_contratacao=6,
    )

    assert client.pages == [1, 2]
    assert stats.paginas_processadas == 2
    assert stats.lidos == 2
    assert stats.inseridos == 2
    assert (
        db_session.scalar(select(func.count()).select_from(PNCPContractingRecord)) == 2
    )


@pytest.mark.asyncio
async def test_sync_updates_existing_record(db_session: Session) -> None:
    client = FakePNCPClient()
    service = PNCPSyncService(db_session, client=client, page_delay_seconds=0)
    kwargs = {
        "data_inicial": date(2026, 7, 1),
        "data_final": date(2026, 7, 20),
        "codigo_modalidade_contratacao": 6,
        "limite_paginas": 1,
    }

    first = await service.synchronize(**kwargs)
    second = await service.synchronize(**kwargs)

    assert first.inseridos == 1
    assert second.atualizados == 1
    assert (
        db_session.scalar(select(func.count()).select_from(PNCPContractingRecord)) == 1
    )
