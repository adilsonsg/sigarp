from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.models.pncp_processing_run import (
    PNCPOpportunityAssessmentHistoryRecord,
    PNCPProcessingRunRecord,
)
from app.schemas.pncp_opportunities import PNCPOpportunityAssessmentInput


class PNCPAuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def start_run(
        self,
        *,
        tipo: str,
        perfil: str | None,
        perfil_versao: str | None,
        analisador_versao: str | None,
        parametros: dict[str, Any],
    ) -> PNCPProcessingRunRecord:
        run = PNCPProcessingRunRecord(
            tipo=tipo,
            status="EM_EXECUCAO",
            perfil=perfil,
            perfil_versao=perfil_versao,
            analisador_versao=analisador_versao,
            parametros=parametros,
        )
        self.db.add(run)
        self.db.flush()
        return run

    def finish_run(
        self,
        run: PNCPProcessingRunRecord,
        *,
        status: str,
        estatisticas: dict[str, Any],
        erro: str | None = None,
    ) -> None:
        run.status = status
        run.estatisticas = estatisticas
        run.erro = erro
        run.concluido_em = datetime.now(UTC)
        self.db.flush()

    def record_assessment(
        self,
        *,
        run_id: int,
        assessment: PNCPOpportunityAssessmentRecord,
        payload: PNCPOpportunityAssessmentInput,
    ) -> PNCPOpportunityAssessmentHistoryRecord:
        history = PNCPOpportunityAssessmentHistoryRecord(
            assessment_id=assessment.id,
            contracting_id=payload.contracting_id,
            execucao_id=run_id,
            perfil=payload.perfil,
            perfil_versao=payload.perfil_versao,
            analisador_versao=payload.analisador_versao,
            classificacao=payload.classificacao,
            pontuacao=payload.pontuacao,
            adequacao_perfil=payload.adequacao_perfil,
            pontuacao_adequacao=payload.pontuacao_adequacao,
            snapshot=payload.model_dump(mode="json"),
            classificado_em=assessment.classificado_em,
        )
        self.db.add(history)
        self.db.flush()
        return history

    def list_runs(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PNCPProcessingRunRecord]:
        statement = (
            select(PNCPProcessingRunRecord)
            .order_by(PNCPProcessingRunRecord.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement))

    def count_runs(self) -> int:
        statement = select(func.count()).select_from(PNCPProcessingRunRecord)
        return int(self.db.scalar(statement) or 0)

    def list_assessment_history(
        self,
        assessment_id: int,
        *,
        skip: int = 0,
        limit: int | None = None,
    ) -> list[PNCPOpportunityAssessmentHistoryRecord]:
        statement = (
            select(PNCPOpportunityAssessmentHistoryRecord)
            .where(
                PNCPOpportunityAssessmentHistoryRecord.assessment_id == assessment_id
            )
            .order_by(PNCPOpportunityAssessmentHistoryRecord.id.desc())
            .offset(skip)
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.db.scalars(statement))

    def count_assessment_history(self, assessment_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(PNCPOpportunityAssessmentHistoryRecord)
            .where(
                PNCPOpportunityAssessmentHistoryRecord.assessment_id == assessment_id
            )
        )
        return int(self.db.scalar(statement) or 0)
