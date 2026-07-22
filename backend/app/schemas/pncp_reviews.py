from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReviewDecision(StrEnum):
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"
    EXIGE_ANALISE_ADICIONAL = "EXIGE_ANALISE_ADICIONAL"


class PNCPOpportunityReviewCreate(BaseModel):
    decisao: ReviewDecision
    justificativa: str = Field(min_length=10, max_length=2000)


class PNCPOpportunityReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: int
    execucao_id: int | None = None
    actor_subject: str
    actor_name: str
    actor_role: str
    decisao: ReviewDecision
    justificativa: str
    resultado_avaliado: dict[str, Any]
    valor_anterior: dict[str, Any]
    valor_novo: dict[str, Any]
    criado_em: datetime
