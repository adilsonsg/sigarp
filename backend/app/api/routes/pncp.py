from typing import Annotated

from fastapi import APIRouter, Depends

from app.collectors.pncp.schemas import PNCPSearchRequest, PNCPSearchResponse
from app.collectors.pncp.service import PNCPSearchService

router = APIRouter(prefix="/pncp", tags=["PNCP"])


def get_pncp_search_service() -> PNCPSearchService:
    return PNCPSearchService()


@router.post(
    "/contratacoes/pesquisar",
    response_model=PNCPSearchResponse,
    response_model_by_alias=False,
    summary="Pesquisar contratações publicadas no PNCP",
)
async def search_contractings(
    request: PNCPSearchRequest,
    service: Annotated[PNCPSearchService, Depends(get_pncp_search_service)],
) -> PNCPSearchResponse:
    return await service.search_contractings(request)
