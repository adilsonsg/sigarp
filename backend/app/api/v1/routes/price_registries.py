from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.pagination import create_page
from app.api.responses import COMMON_ERROR_RESPONSES
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.pagination import Page
from app.schemas.pncp_price_registry import (
    PNCPPriceRegistryItemResponse,
    PNCPPriceRegistryItemSupplierResponse,
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
    quantidade_minima: Decimal | None = Query(default=None, gt=0),
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
        "minimum_quantity": quantidade_minima,
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
            itens=[
                PNCPPriceRegistryItemResponse(
                    numero_item=registry_item.numero_item,
                    descricao=registry_item.descricao,
                    quantidade_registrada=registry_item.quantidade_registrada,
                    quantidade_empenhada=registry_item.quantidade_empenhada,
                    saldo_estimado=registry_item.saldo_estimado,
                    limite_adesao=registry_item.limite_adesao,
                    valor_unitario=registry_item.valor_unitario,
                    fornecedor=(
                        PNCPPriceRegistryItemSupplierResponse(
                            cnpj=registry_item.fornecedor.cnpj,
                            razao_social=registry_item.fornecedor.razao_social,
                        )
                        if registry_item.fornecedor
                        else None
                    ),
                    disponibilidade=_availability(
                        registry_item.quantidade_registrada,
                        registry_item.saldo_estimado,
                        registry_item.limite_adesao,
                        quantidade_minima,
                    ),
                )
                for registry_item in record.itens
                if _item_matches(
                    registry_item,
                    term=termo,
                    minimum_quantity=quantidade_minima,
                    object_matches=(
                        bool(termo)
                        and termo.strip().casefold() in record.objeto.casefold()
                    ),
                )
            ],
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


def _item_matches(
    item,  # type: ignore[no-untyped-def]
    *,
    term: str | None,
    minimum_quantity: Decimal | None,
    object_matches: bool,
) -> bool:
    if minimum_quantity is not None and (
        item.quantidade_registrada is None
        or item.quantidade_registrada < minimum_quantity
    ):
        return False
    if not term or object_matches:
        return True
    normalized = term.strip().casefold()
    searchable = " ".join(
        filter(
            None,
            [item.descricao, item.fabricante, item.marca, item.modelo],
        )
    ).casefold()
    return normalized in searchable


def _availability(
    registered: Decimal | None,
    estimated_balance: Decimal | None,
    adhesion_limit: Decimal | None,
    requested: Decimal | None,
) -> str:
    if requested is None:
        return "NAO_AVALIADA"
    if registered is None or registered < requested:
        return "NAO_ATENDE"
    if estimated_balance is not None and estimated_balance < requested:
        return "NAO_ATENDE"
    if adhesion_limit is None or adhesion_limit <= 0:
        return "CONFIRMAR_COM_ORGAO"
    if adhesion_limit < requested:
        return "NAO_ATENDE"
    return "ATENDE"
