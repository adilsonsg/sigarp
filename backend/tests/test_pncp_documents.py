from datetime import datetime

import httpx
import pytest

from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.config import PNCPConfig
from app.sync.pncp_document_sync import PNCPDocumentSyncService


@pytest.mark.asyncio
async def test_client_builds_contracting_documents_endpoint() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=[], request=request)

    config = PNCPConfig(
        base_url="https://pncp.test",
        timeout_seconds=1,
        max_retries=0,
        backoff_seconds=0.01,
        user_agent="SIGARP-Test",
    )
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(config, client=http_client)
        await client.buscar_documentos_contratacao(
            cnpj="04.264.173/0001-78",
            ano=2026,
            sequencial=54,
        )

    assert captured_request is not None
    assert captured_request.url.path == (
        "/api/pncp/v1/orgaos/04264173000178/compras/2026/54/arquivos"
    )
    assert captured_request.url.query == b""


def test_extract_documents_accepts_list_and_wrapper() -> None:
    one = {"sequencialDocumento": 1, "titulo": "Edital"}
    assert PNCPDocumentSyncService._extract_documents([one]) == [one]
    assert PNCPDocumentSyncService._extract_documents({"documentos": [one]}) == [one]


def test_normalize_document() -> None:
    result = PNCPDocumentSyncService._normalize(
        10,
        {
            "sequencialDocumento": 2,
            "titulo": "Termo de Referência",
            "tipoDocumentoId": 2,
            "tipoDocumentoNome": "Edital",
            "url": "https://pncp.test/documento.pdf",
            "dataPublicacaoPncp": "2026-07-21T10:30:00Z",
        },
    )
    assert result is not None
    assert result.contracting_id == 10
    assert result.sequencial_documento == 2
    assert result.data_publicacao_pncp == datetime.fromisoformat(
        "2026-07-21T10:30:00+00:00"
    )


class FakeDocumentClient:
    def __init__(self, payload):  # type: ignore[no-untyped-def]
        self.payload = payload
        self.calls = 0

    async def buscar_documentos_contratacao(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self.payload

    async def close(self) -> None:
        raise AssertionError("Injected client must not be closed")


@pytest.mark.asyncio
async def test_sync_documents_persists_and_marks_contracting(db_session) -> None:
    from sqlalchemy import func, select

    from app.models.pncp_contracting import PNCPContractingRecord
    from app.models.pncp_contracting_document import (
        PNCPContractingDocumentRecord,
    )

    contracting = PNCPContractingRecord(
        numero_controle_pncp="04264173000178-1-000054/2026",
        ano_compra=2026,
        orgao_cnpj="04264173000178",
        objeto_compra="Aquisição de projetores",
        dados_fonte={"sequencialCompra": 54},
    )
    db_session.add(contracting)
    db_session.commit()

    client = FakeDocumentClient(
        [
            {
                "sequencialDocumento": 1,
                "titulo": "Edital",
                "tipoDocumentoNome": "Edital",
            }
        ]
    )
    stats = await PNCPDocumentSyncService(
        db_session, client=client, request_delay_seconds=0
    ).synchronize(somente_sem_documentos=True)

    assert stats.contratacoes_processadas == 1
    assert stats.inseridos == 1
    assert contracting.documentos_sincronizados_em is not None
    assert contracting.documentos_quantidade == 1
    assert (
        db_session.scalar(
            select(func.count()).select_from(PNCPContractingDocumentRecord)
        )
        == 1
    )

    await PNCPDocumentSyncService(
        db_session, client=client, request_delay_seconds=0
    ).synchronize(somente_sem_documentos=True)
    assert client.calls == 1
