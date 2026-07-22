from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pncp_opportunity_assessment import (
    PNCPOpportunityAssessmentRecord,
)
from app.schemas.pncp_opportunities import PNCPOpportunityAssessmentInput


class PNCPOpportunityAssessmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(
        self, contracting_id: int, perfil: str, perfil_versao: str
    ) -> PNCPOpportunityAssessmentRecord | None:
        return self.db.scalar(
            select(PNCPOpportunityAssessmentRecord).where(
                PNCPOpportunityAssessmentRecord.contracting_id == contracting_id,
                PNCPOpportunityAssessmentRecord.perfil == perfil,
                PNCPOpportunityAssessmentRecord.perfil_versao == perfil_versao,
            )
        )

    def upsert(
        self, payload: PNCPOpportunityAssessmentInput
    ) -> tuple[PNCPOpportunityAssessmentRecord, bool]:
        record = self.get(
            payload.contracting_id,
            payload.perfil,
            payload.perfil_versao,
        )
        created = record is None
        data = payload.model_dump()
        if record is None:
            record = PNCPOpportunityAssessmentRecord(**data)
            self.db.add(record)
        else:
            for field, value in data.items():
                setattr(record, field, value)
        record.classificado_em = datetime.now(UTC)
        self.db.flush()
        return record, created
