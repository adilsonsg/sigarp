import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.pncp.client import PNCPClient
from app.models.pncp_contracting import PNCPContractingRecord
from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.repositories.pncp_contracting_document_repository import (
    PNCPContractingDocumentRepository,
)
from app.schemas.pncp_documents import (
    PNCPContractingDocumentInput,
    PNCPDocumentSyncStats,
)
from app.services.projector_profile_analyzer import ProjectorProfileAnalyzer

logger = logging.getLogger(__name__)


class PNCPDocumentSyncService:
    def __init__(
        self,
        db: Session,
        client: PNCPClient | None = None,
        request_delay_seconds: float = 2.0,
    ) -> None:
        self.db = db
        self.repository = PNCPContractingDocumentRepository(db)
        self._client = client
        self.request_delay_seconds = max(request_delay_seconds, 0.0)

    async def synchronize(
        self,
        *,
        numero_controle_pncp: str | None = None,
        somente_sem_documentos: bool = False,
        somente_candidatas: bool = False,
        limite_contratacoes: int | None = None,
    ) -> PNCPDocumentSyncStats:
        stats = PNCPDocumentSyncStats()
        owns_client = self._client is None
        client = self._client or PNCPClient()
        try:
            records = self._contractings(
                numero_controle_pncp=numero_controle_pncp,
                somente_sem_documentos=somente_sem_documentos,
                somente_candidatas=somente_candidatas,
                limite_contratacoes=limite_contratacoes,
            )
            for contracting in records:
                identifiers = self._identifiers(contracting)
                if identifiers is None:
                    stats.ignorados += 1
                    continue
                cnpj, ano, sequencial = identifiers
                try:
                    payload = await client.buscar_documentos_contratacao(
                        cnpj=cnpj,
                        ano=ano,
                        sequencial=sequencial,
                    )
                    documents = self._extract_documents(payload)
                    for document in documents:
                        stats.documentos_lidos += 1
                        normalized = self._normalize(contracting.id, document)
                        if normalized is None:
                            stats.ignorados += 1
                            continue
                        _, created = self.repository.upsert(normalized)
                        if created:
                            stats.inseridos += 1
                        else:
                            stats.atualizados += 1
                    contracting.documentos_sincronizados_em = datetime.now(UTC)
                    contracting.documentos_quantidade = len(documents)
                    self.db.commit()
                    stats.contratacoes_processadas += 1
                except Exception:
                    logger.exception(
                        "Falha ao sincronizar documentos PNCP",
                        extra={
                            "numero_controle_pncp": (contracting.numero_controle_pncp)
                        },
                    )
                    stats.erros += 1
                    self.db.rollback()
                if self.request_delay_seconds:
                    await asyncio.sleep(self.request_delay_seconds)
        finally:
            if owns_client:
                await client.close()
        return stats

    def _contractings(
        self,
        *,
        numero_controle_pncp: str | None,
        somente_sem_documentos: bool,
        somente_candidatas: bool,
        limite_contratacoes: int | None,
    ) -> list[PNCPContractingRecord]:
        statement = select(PNCPContractingRecord).order_by(PNCPContractingRecord.id)
        if numero_controle_pncp:
            statement = statement.where(
                PNCPContractingRecord.numero_controle_pncp == numero_controle_pncp
            )
        if somente_sem_documentos:
            statement = statement.where(
                PNCPContractingRecord.documentos_sincronizados_em.is_(None)
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
                PNCPOpportunityAssessmentRecord.classificacao == "CANDIDATA_DOCUMENTO",
            )
        if limite_contratacoes:
            statement = statement.limit(limite_contratacoes)
        return list(self.db.scalars(statement).unique())

    @staticmethod
    def _identifiers(
        record: PNCPContractingRecord,
    ) -> tuple[str, int, int] | None:
        raw = record.dados_fonte or {}
        cnpj = record.orgao_cnpj or ((raw.get("orgaoEntidade") or {}).get("cnpj"))
        ano = record.ano_compra or raw.get("anoCompra")
        sequencial = raw.get("sequencialCompra")
        if sequencial is None:
            try:
                sequencial = int(
                    record.numero_controle_pncp.split("-1-")[1].split("/")[0]
                )
            except (IndexError, ValueError):
                return None
        if not cnpj or not ano:
            return None
        return str(cnpj), int(ano), int(sequencial)

    @staticmethod
    def _extract_documents(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if not isinstance(payload, dict):
            return []
        documents = (
            payload.get("documentos")
            or payload.get("Documentos")
            or payload.get("data")
            or payload.get("content")
            or []
        )
        return [item for item in documents if isinstance(item, dict)]

    @staticmethod
    def _datetime(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    @classmethod
    def _normalize(
        cls, contracting_id: int, document: dict[str, Any]
    ) -> PNCPContractingDocumentInput | None:
        sequencial = document.get("sequencialDocumento")
        if sequencial is None:
            return None
        return PNCPContractingDocumentInput(
            contracting_id=contracting_id,
            sequencial_documento=int(sequencial),
            titulo=document.get("titulo"),
            tipo_documento_id=document.get("tipoDocumentoId"),
            tipo_documento_nome=document.get("tipoDocumentoNome"),
            url=document.get("url"),
            uri=document.get("uri"),
            data_publicacao_pncp=cls._datetime(document.get("dataPublicacaoPncp")),
            dados_fonte=document,
        )
