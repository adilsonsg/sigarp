from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.pagination import create_page
from app.api.responses import COMMON_ERROR_RESPONSES
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.pagination import Page
from app.schemas.pncp_price_registry import (
    PNCPPriceRegistryOrganizationResponse,
    PNCPPriceRegistryResponse,
)
from app.security.authentication import require_minimum_role
from app.security.models import AccessRole

router = APIRouter(
    prefix="/atas",
    tags=["Atas de Registro de Preços"],
    dependencies=[Depends(require_minimum_role(AccessRole.LEITOR))],
    responses=COMMON_ERROR_RESPONSES,
)


@router.get("", response_model=Page[PNCPPriceRegistryResponse])
def list_price_registries(
    db: Annotated[Session, Depends(get_db)],
    termo: str | None = Query(default=None, min_length=2, max_length=200),
    somente_vigentes: bool = Query(default=True),
    esfera: str | None = Query(default="federal"),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    vigente_em: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Page[PNCPPriceRegistryResponse]:
    repository = PriceRegistryRepository(db)
    filters = {
        "term": termo,
        "only_active": somente_vigentes,
        "sphere": esfera,
        "uf": uf,
        "valid_on": vigente_em,
    }
    records = repository.search(
        **filters,
        skip=(page - 1) * page_size,
        limit=page_size,
    )
    items = [
        PNCPPriceRegistryResponse(
            id=record.id,
            numero_controle_pncp=record.numero_controle_pncp,
            numero_ata=record.numero_ata,
            numero_processo=record.numero_processo,
            objeto=record.objeto,
            vigencia_inicio=record.vigencia_inicio,
            vigencia_fim=record.vigencia_fim,
            situacao=record.situacao,
            url_pncp=record.url_pncp,
            orgao=PNCPPriceRegistryOrganizationResponse(
                nome=record.orgao_gerenciador.nome,
                cnpj=record.orgao_gerenciador.cnpj,
                esfera=record.orgao_gerenciador.esfera,
                uf=record.orgao_gerenciador.uf,
                municipio=record.orgao_gerenciador.municipio,
            ),
            itens_quantidade=len(record.itens),
            possibilidade_adesao=(
                record.dados_fonte.get("possibilidadeAdesao")
                if record.dados_fonte
                else None
            ),
        )
        for record in records
    ]
    return create_page(
        items,
        page=page,
        page_size=page_size,
        total=repository.count(**filters),
    )
