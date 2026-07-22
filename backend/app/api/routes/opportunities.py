from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.pncp_opportunities import PNCPOpportunityResponse
from app.services.pncp_opportunity_service import PNCPOpportunityService

router = APIRouter(prefix="/pncp/oportunidades", tags=["Oportunidades PNCP"])


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
