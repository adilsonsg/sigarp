from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AccessDeniedError, ResourceNotFoundError
from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.models.pncp_opportunity_review import PNCPOpportunityReviewRecord
from app.schemas.pncp_reviews import PNCPOpportunityReviewCreate
from app.security.models import AuthenticatedPrincipal


class PNCPOpportunityReviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def review(
        self,
        assessment_id: int,
        payload: PNCPOpportunityReviewCreate,
        principal: AuthenticatedPrincipal,
    ) -> PNCPOpportunityReviewRecord:
        assessment = self.db.scalar(
            select(PNCPOpportunityAssessmentRecord)
            .where(PNCPOpportunityAssessmentRecord.id == assessment_id)
            .with_for_update()
        )
        if assessment is None:
            raise ResourceNotFoundError("Avaliação não encontrada.")
        if principal.role is None:
            raise AccessDeniedError()

        previous = {
            "revisao_status": assessment.revisao_status,
            "revisado_por": assessment.revisado_por,
            "revisado_em": (
                assessment.revisado_em.isoformat() if assessment.revisado_em else None
            ),
        }
        reviewed_at = datetime.now(UTC)
        current = {
            "revisao_status": payload.decisao.value,
            "revisado_por": principal.subject,
            "revisado_em": reviewed_at.isoformat(),
        }
        assessed_result = {
            "classificacao": assessment.classificacao,
            "pontuacao": assessment.pontuacao,
            "adequacao_perfil": assessment.adequacao_perfil,
            "pontuacao_adequacao": assessment.pontuacao_adequacao,
            "perfil": assessment.perfil,
            "perfil_versao": assessment.perfil_versao,
            "analisador_versao": assessment.analisador_versao,
            "classificado_em": assessment.classificado_em.isoformat(),
        }
        review = PNCPOpportunityReviewRecord(
            assessment_id=assessment.id,
            execucao_id=assessment.ultima_execucao_id,
            actor_subject=principal.subject,
            actor_name=principal.name,
            actor_role=principal.role.value,
            decisao=payload.decisao.value,
            justificativa=payload.justificativa,
            resultado_avaliado=assessed_result,
            valor_anterior=previous,
            valor_novo=current,
        )
        assessment.revisao_status = payload.decisao.value
        assessment.revisado_por = principal.subject
        assessment.revisado_em = reviewed_at
        self.db.add(review)
        self.db.flush()
        return review

    def list_by_assessment(
        self, assessment_id: int
    ) -> list[PNCPOpportunityReviewRecord]:
        assessment_exists = self.db.scalar(
            select(PNCPOpportunityAssessmentRecord.id).where(
                PNCPOpportunityAssessmentRecord.id == assessment_id
            )
        )
        if assessment_exists is None:
            raise ResourceNotFoundError("Avaliação não encontrada.")
        statement = (
            select(PNCPOpportunityReviewRecord)
            .where(PNCPOpportunityReviewRecord.assessment_id == assessment_id)
            .order_by(PNCPOpportunityReviewRecord.id.desc())
        )
        return list(self.db.scalars(statement))
