from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.collectors.pncp.schemas import PNCPSearchRequest, PNCPSearchResponse
from app.collectors.pncp.service import PNCPSearchService
from app.security.authentication import require_minimum_role
from app.security.models import AccessRole

router = APIRouter(
    prefix="/pncp",
    tags=["PNCP"],
    dependencies=[Depends(require_minimum_role(AccessRole.LEITOR))],
)


def get_pncp_search_service() -> PNCPSearchService:
    return PNCPSearchService()


@router.get(
    "/search",
    response_model=PNCPSearchResponse,
    response_model_by_alias=False,
    summary="Pesquisar contratações publicadas no PNCP",
    description=(
        "Atalho de consulta por parâmetros de URL. O termo é filtrado localmente "
        "sobre o objeto e as informações complementares das contratações retornadas."
    ),
)
async def search_contractings_get(
    service: Annotated[PNCPSearchService, Depends(get_pncp_search_service)],
    termo: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    data_inicial: date = Query(...),
    data_final: date = Query(...),
    codigo_modalidade_contratacao: int = Query(..., ge=1),
    uf: Annotated[str | None, Query(min_length=2, max_length=2)] = None,
    pagina: int = Query(default=1, ge=1),
    somente_srp: bool = Query(default=False),
) -> PNCPSearchResponse:
    try:
        request = PNCPSearchRequest(
            palavra_chave=termo,
            data_inicial=data_inicial,
            data_final=data_final,
            codigo_modalidade_contratacao=codigo_modalidade_contratacao,
            uf=uf,
            pagina=pagina,
            somente_srp=somente_srp,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    return await service.search_contractings(request)


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
