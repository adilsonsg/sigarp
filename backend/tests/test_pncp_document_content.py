import httpx
import pytest
from pypdf import PdfWriter
from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.models.pncp_contracting_document import PNCPContractingDocumentRecord
from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.services.pncp_document_content_service import (
    PNCPDocumentContentService,
)


class FakeDownloadClient:
    def __init__(self, content: bytes, content_type: str = "text/plain"):
        self.content = content
        self.content_type = content_type
        self.calls = 0

    async def baixar_documento(self, url: str) -> httpx.Response:
        self.calls += 1
        request = httpx.Request("GET", url)
        return httpx.Response(
            200,
            content=self.content,
            headers={"content-type": self.content_type},
            request=request,
        )

    async def close(self) -> None:
        raise AssertionError("Injected client must not be closed")


def test_extract_plain_text() -> None:
    service = PNCPDocumentContentService.__new__(PNCPDocumentContentService)
    service.max_pages = 100
    service.max_bytes = 1_000_000
    result = service._extract_content(
        b"Projetor laser Full HD",
        content_type="text/plain",
        filename="edital.txt",
    )
    assert result.status == "SUCESSO"
    assert "Projetor" in result.text


def test_extract_blank_pdf_marks_sem_texto() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    from io import BytesIO

    buffer = BytesIO()
    writer.write(buffer)
    service = PNCPDocumentContentService.__new__(PNCPDocumentContentService)
    service.max_pages = 100
    service.max_bytes = 1_000_000
    result = service._extract_content(
        buffer.getvalue(),
        content_type="application/pdf",
        filename="edital.pdf",
    )
    assert result.status == "SEM_TEXTO"
    assert result.pages == 1


@pytest.mark.asyncio
async def test_analyze_document_persists_text(db_session: Session) -> None:
    contracting = PNCPContractingRecord(
        numero_controle_pncp="04264173000178-1-000054/2026",
        objeto_compra="Aquisição de projetores",
    )
    db_session.add(contracting)
    db_session.flush()
    db_session.add(
        PNCPContractingDocumentRecord(
            contracting_id=contracting.id,
            sequencial_documento=2,
            titulo="Edital",
            url="https://pncp.test/edital.txt",
        )
    )
    db_session.add(
        PNCPOpportunityAssessmentRecord(
            contracting_id=contracting.id,
            perfil="projetores",
            perfil_versao="1.0.0",
            classificacao="CANDIDATA_DOCUMENTO",
            pontuacao=60,
        )
    )
    db_session.commit()

    client = FakeDownloadClient(b"Projetor laser Full HD Wi-Fi")
    stats = await PNCPDocumentContentService(
        db_session,
        client=client,
        request_delay_seconds=0,
        max_bytes=10000,
        max_text_chars=10000,
        max_pages=100,
    ).analyze(somente_candidatas=True, somente_pendentes=True)

    document = db_session.query(PNCPContractingDocumentRecord).one()
    assert stats.documentos_processados == 1
    assert stats.sucessos == 1
    assert document.extracao_status == "SUCESSO"
    assert document.texto_extraido == "Projetor laser Full HD Wi-Fi"
    assert document.conteudo_sha256 is not None
    assert document.extrator_versao == "1.0.0"
