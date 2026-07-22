from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.pncp_opportunities import (
    PNCPOpportunityHistoryResponse,
    PNCPOpportunityResponse,
    PNCPProcessingRunResponse,
)
from app.services.pncp_opportunity_service import PNCPOpportunityService

router = APIRouter(prefix="/pncp/oportunidades", tags=["Oportunidades PNCP"])


@router.get("/execucoes", response_model=list[PNCPProcessingRunResponse])
def list_processing_runs(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=100, ge=1, le=500),
) -> list[PNCPProcessingRunResponse]:
    return PNCPOpportunityService(db).list_processing_runs(limit=limit)


@router.get(
    "/{assessment_id}/historico",
    response_model=list[PNCPOpportunityHistoryResponse],
)
def list_assessment_history(
    assessment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[PNCPOpportunityHistoryResponse]:
    return PNCPOpportunityService(db).list_assessment_history(assessment_id)


@router.get("", response_model=list[PNCPOpportunityResponse])
def list_opportunities(
    db: Annotated[Session, Depends(get_db)],
    perfil: str = Query(default="projetores", min_length=2, max_length=50),
    perfil_versao: str | None = Query(default=None, min_length=5, max_length=30),
    classificacao: str | None = Query(default=None),
    adequacao: str | None = Query(default=None),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[PNCPOpportunityResponse]:
    return PNCPOpportunityService(db).list_opportunities(
        perfil=perfil,
        perfil_versao=perfil_versao,
        classificacao=classificacao,
        adequacao=adequacao,
        uf=uf,
        skip=skip,
        limit=limit,
    )
