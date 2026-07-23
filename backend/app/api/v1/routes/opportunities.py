from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.pagination import create_page
from app.api.responses import COMMON_ERROR_RESPONSES
from app.schemas.pagination import Page
from app.schemas.pncp_opportunities import (
    PNCPOpportunityHistoryResponse,
    PNCPOpportunityResponse,
    PNCPProcessingRunResponse,
)
from app.schemas.pncp_reviews import (
    PNCPOpportunityReviewCreate,
    PNCPOpportunityReviewResponse,
)
from app.security.authentication import require_minimum_role
from app.security.models import AccessRole, AuthenticatedPrincipal
from app.services.pncp_opportunity_review_service import (
    PNCPOpportunityReviewService,
)
from app.services.pncp_opportunity_service import PNCPOpportunityService

router = APIRouter(
    prefix="/pncp/oportunidades",
    tags=["Oportunidades PNCP"],
    dependencies=[Depends(require_minimum_role(AccessRole.LEITOR))],
    responses=COMMON_ERROR_RESPONSES,
)


@router.get("/execucoes", response_model=Page[PNCPProcessingRunResponse])
def list_processing_runs(
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Page[PNCPProcessingRunResponse]:
    service = PNCPOpportunityService(db)
    return create_page(
        service.list_processing_runs(
            skip=(page - 1) * page_size,
            limit=page_size,
        ),
        page=page,
        page_size=page_size,
        total=service.count_processing_runs(),
    )


@router.get(
    "/{assessment_id}/historico",
    response_model=Page[PNCPOpportunityHistoryResponse],
)
def list_assessment_history(
    assessment_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Page[PNCPOpportunityHistoryResponse]:
    service = PNCPOpportunityService(db)
    return create_page(
        service.list_assessment_history(
            assessment_id,
            skip=(page - 1) * page_size,
            limit=page_size,
        ),
        page=page,
        page_size=page_size,
        total=service.count_assessment_history(assessment_id),
    )


@router.patch(
    "/{assessment_id}/revisao",
    response_model=PNCPOpportunityReviewResponse,
)
def review_opportunity(
    assessment_id: int,
    payload: PNCPOpportunityReviewCreate,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_minimum_role(AccessRole.ANALISTA)),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> PNCPOpportunityReviewResponse:
    return PNCPOpportunityReviewService(db).review(
        assessment_id,
        payload,
        principal,
    )


@router.get(
    "/{assessment_id}/revisoes",
    response_model=Page[PNCPOpportunityReviewResponse],
)
def list_opportunity_reviews(
    assessment_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Page[PNCPOpportunityReviewResponse]:
    service = PNCPOpportunityReviewService(db)
    return create_page(
        service.list_by_assessment(
            assessment_id,
            skip=(page - 1) * page_size,
            limit=page_size,
        ),
        page=page,
        page_size=page_size,
        total=service.count_by_assessment(assessment_id),
    )


@router.get("", response_model=Page[PNCPOpportunityResponse])
def list_opportunities(
    db: Annotated[Session, Depends(get_db)],
    perfil: str = Query(default="projetores", min_length=2, max_length=50),
    perfil_versao: str | None = Query(default=None, min_length=5, max_length=30),
    classificacao: str | None = Query(default=None),
    adequacao: str | None = Query(default=None),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Page[PNCPOpportunityResponse]:
    service = PNCPOpportunityService(db)
    filters = {
        "perfil": perfil,
        "perfil_versao": perfil_versao,
        "classificacao": classificacao,
        "adequacao": adequacao,
        "uf": uf,
    }
    return create_page(
        service.list_opportunities(
            **filters,
            skip=(page - 1) * page_size,
            limit=page_size,
        ),
        page=page,
        page_size=page_size,
        total=service.count_opportunities(**filters),
    )
