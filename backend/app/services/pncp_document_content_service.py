from __future__ import annotations

import asyncio
import hashlib
import io
import logging
import re
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import Message
from pathlib import PurePosixPath

import httpx
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.collectors.pncp.client import PNCPClient
from app.core.config import settings
from app.models.pncp_contracting import PNCPContractingRecord
from app.models.pncp_contracting_document import PNCPContractingDocumentRecord
from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.schemas.pncp_documents import PNCPDocumentAnalysisStats
from app.services.projector_profile_analyzer import ProjectorProfileAnalyzer

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ExtractedDocument:
    status: str
    text: str = ""
    pages: int = 0
    error: str | None = None


class PNCPDocumentContentService:
    TEXT_CONTENT_TYPES = (
        "text/",
        "application/json",
        "application/xml",
        "application/xhtml+xml",
    )

    def __init__(
        self,
        db: Session,
        client: PNCPClient | None = None,
        request_delay_seconds: float = 2.0,
        max_bytes: int | None = None,
        max_text_chars: int | None = None,
        max_pages: int | None = None,
    ) -> None:
        self.db = db
        self._client = client
        self.request_delay_seconds = max(request_delay_seconds, 0.0)
        self.max_bytes = max_bytes or settings.pncp_document_max_bytes
        self.max_text_chars = max_text_chars or settings.pncp_document_max_text_chars
        self.max_pages = max_pages or settings.pncp_document_max_pages

    async def analyze(
        self,
        *,
        numero_controle_pncp: str | None = None,
        somente_candidatas: bool = False,
        somente_pendentes: bool = False,
        limite_documentos: int | None = None,
    ) -> PNCPDocumentAnalysisStats:
        stats = PNCPDocumentAnalysisStats()
        owns_client = self._client is None
        client = self._client or PNCPClient()
        try:
            for document in self._documents(
                numero_controle_pncp=numero_controle_pncp,
                somente_candidatas=somente_candidatas,
                somente_pendentes=somente_pendentes,
                limite_documentos=limite_documentos,
            ):
                url = document.url or document.uri
                if not url:
                    document.extracao_status = "SEM_URL"
                    document.extracao_erro = "Documento sem URL ou URI."
                    document.conteudo_analisado_em = datetime.now(UTC)
                    self.db.commit()
                    stats.ignorados += 1
                    continue

                try:
                    response = await client.baixar_documento(url)
                    self._persist_response(document, response)
                    self.db.commit()
                    stats.documentos_processados += 1
                    self._increment(stats, document.extracao_status)
                except Exception as exc:
                    self.db.rollback()
                    current = self.db.get(PNCPContractingDocumentRecord, document.id)
                    if current is not None:
                        current.extracao_status = "ERRO"
                        current.extracao_erro = str(exc)[:2000]
                        current.conteudo_analisado_em = datetime.now(UTC)
                        self.db.commit()
                    stats.erros += 1
                    logger.exception(
                        "Falha ao analisar documento PNCP",
                        extra={"document_id": document.id, "url": url},
                    )

                if self.request_delay_seconds:
                    await asyncio.sleep(self.request_delay_seconds)
        finally:
            if owns_client:
                await client.close()
        return stats

    def _documents(
        self,
        *,
        numero_controle_pncp: str | None,
        somente_candidatas: bool,
        somente_pendentes: bool,
        limite_documentos: int | None,
    ) -> list[PNCPContractingDocumentRecord]:
        statement = (
            select(PNCPContractingDocumentRecord)
            .join(PNCPContractingDocumentRecord.contracting)
            .options(selectinload(PNCPContractingDocumentRecord.contracting))
            .order_by(PNCPContractingDocumentRecord.id)
        )
        if numero_controle_pncp:
            statement = statement.where(
                PNCPContractingRecord.numero_controle_pncp == numero_controle_pncp
            )
        if somente_pendentes:
            statement = statement.where(
                PNCPContractingDocumentRecord.conteudo_analisado_em.is_(None)
            )
        if somente_candidatas:
            statement = statement.join(
                PNCPOpportunityAssessmentRecord,
                PNCPOpportunityAssessmentRecord.contracting_id
                == PNCPContractingRecord.id,
            ).where(
                PNCPOpportunityAssessmentRecord.perfil == "projetores",
                PNCPOpportunityAssessmentRecord.perfil_versao
                == ProjectorProfileAnalyzer.PROFILE.versao,
                PNCPOpportunityAssessmentRecord.classificacao.in_(
                    ["CANDIDATA_DOCUMENTO", "CONFIRMADA_DOCUMENTO"]
                ),
            )
        if limite_documentos:
            statement = statement.limit(limite_documentos)
        return list(self.db.scalars(statement).unique())

    def _persist_response(
        self,
        document: PNCPContractingDocumentRecord,
        response: httpx.Response,
    ) -> None:
        content = response.content
        content_type = response.headers.get("content-type", "").split(";")[0]
        content_type = content_type.strip().lower()
        document.nome_arquivo = self._filename(response, document)
        document.conteudo_tipo = content_type or None
        document.conteudo_tamanho = len(content)
        document.conteudo_sha256 = hashlib.sha256(content).hexdigest()
        document.conteudo_analisado_em = datetime.now(UTC)
        document.extracao_erro = None

        if len(content) > self.max_bytes:
            document.extracao_status = "LIMITE_EXCEDIDO"
            document.extracao_erro = (
                f"Documento com {len(content)} bytes; limite {self.max_bytes}."
            )
            document.texto_extraido = None
            document.texto_caracteres = 0
            document.paginas_extraidas = 0
            return

        extracted = self._extract_content(
            content,
            content_type=content_type,
            filename=document.nome_arquivo,
        )
        text = self._clean_text(extracted.text)
        document.extracao_status = extracted.status
        document.extracao_erro = extracted.error
        document.texto_caracteres = len(text)
        document.paginas_extraidas = extracted.pages
        document.texto_extraido = text[: self.max_text_chars] or None

    def _extract_content(
        self,
        content: bytes,
        *,
        content_type: str,
        filename: str | None,
    ) -> ExtractedDocument:
        suffix = PurePosixPath(filename or "").suffix.lower()
        if content.startswith(b"%PDF-") or content_type == "application/pdf":
            return self._extract_pdf(content)
        if content.startswith(b"PK\x03\x04") or suffix == ".zip":
            return self._extract_zip(content)
        if content_type.startswith(self.TEXT_CONTENT_TYPES) or suffix in {
            ".txt",
            ".html",
            ".htm",
            ".xml",
            ".json",
            ".csv",
        }:
            text = self._decode_text(content)
            return ExtractedDocument(
                status="SUCESSO" if text.strip() else "SEM_TEXTO",
                text=text,
            )
        return ExtractedDocument(
            status="TIPO_NAO_SUPORTADO",
            error=(
                "Tipo de conteúdo não suportado: "
                f"{content_type or suffix or 'desconhecido'}."
            ),
        )

    def _extract_pdf(self, content: bytes) -> ExtractedDocument:
        try:
            reader = PdfReader(io.BytesIO(content), strict=False)
            total_pages = len(reader.pages)
            page_limit = min(total_pages, self.max_pages)
            texts: list[str] = []
            for index in range(page_limit):
                texts.append(reader.pages[index].extract_text() or "")
            text = "\n\n".join(texts)
            if not text.strip():
                return ExtractedDocument(
                    status="SEM_TEXTO",
                    pages=page_limit,
                    error=("PDF sem camada textual; pode ser documento digitalizado."),
                )
            error = None
            if total_pages > self.max_pages:
                error = f"Extração limitada às primeiras {self.max_pages} páginas."
            return ExtractedDocument(
                status="SUCESSO",
                text=text,
                pages=page_limit,
                error=error,
            )
        except Exception as exc:
            return ExtractedDocument(
                status="ERRO",
                error=f"Falha ao extrair PDF: {exc}"[:2000],
            )

    def _extract_zip(self, content: bytes) -> ExtractedDocument:
        texts: list[str] = []
        pages = 0
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                entries = [entry for entry in archive.infolist() if not entry.is_dir()]
                total_uncompressed = sum(entry.file_size for entry in entries)
                if total_uncompressed > self.max_bytes:
                    return ExtractedDocument(
                        status="LIMITE_EXCEDIDO",
                        error=(
                            "Conteúdo descompactado excede o limite de "
                            f"{self.max_bytes} bytes."
                        ),
                    )
                for entry in entries[:100]:
                    nested = archive.read(entry)
                    extracted = self._extract_content(
                        nested,
                        content_type="",
                        filename=entry.filename,
                    )
                    if extracted.status in {"SUCESSO", "SEM_TEXTO"}:
                        if extracted.text:
                            texts.append(
                                f"\n--- {entry.filename} ---\n{extracted.text}"
                            )
                        pages += extracted.pages
            text = "\n".join(texts)
            return ExtractedDocument(
                status="SUCESSO" if text.strip() else "SEM_TEXTO",
                text=text,
                pages=pages,
                error=(None if text.strip() else "ZIP sem conteúdo textual suportado."),
            )
        except Exception as exc:
            return ExtractedDocument(
                status="ERRO",
                error=f"Falha ao extrair ZIP: {exc}"[:2000],
            )

    @staticmethod
    def _decode_text(content: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _filename(
        response: httpx.Response,
        document: PNCPContractingDocumentRecord,
    ) -> str | None:
        disposition = response.headers.get("content-disposition")
        if disposition:
            message = Message()
            message["content-disposition"] = disposition
            filename = message.get_filename()
            if filename:
                return filename
        url_name = PurePosixPath(response.url.path).name
        if "." in url_name:
            return url_name
        return document.titulo

    @staticmethod
    def _increment(
        stats: PNCPDocumentAnalysisStats,
        status: str | None,
    ) -> None:
        if status == "SUCESSO":
            stats.sucessos += 1
        elif status == "SEM_TEXTO":
            stats.sem_texto += 1
        elif status == "TIPO_NAO_SUPORTADO":
            stats.tipos_nao_suportados += 1
        elif status == "LIMITE_EXCEDIDO":
            stats.limites_excedidos += 1
        elif status == "ERRO":
            stats.erros += 1
        else:
            stats.ignorados += 1
