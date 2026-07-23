from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.pagination import create_page
from app.api.responses import COMMON_ERROR_RESPONSES
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.schemas.pagination import Page
from app.security.authentication import require_minimum_role
from app.security.models import AccessRole, AuthenticatedPrincipal
from app.services.organization_service import OrganizationService

router = APIRouter(
    prefix="/orgaos",
    tags=["Órgãos"],
    responses=COMMON_ERROR_RESPONSES,
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_minimum_role(AccessRole.ADMINISTRADOR)),
    ],
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    organization = OrganizationService(db).create(payload)
    return OrganizationResponse.model_validate(organization)


@router.get("", response_model=Page[OrganizationResponse])
def list_organizations(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_minimum_role(AccessRole.LEITOR)),
    ],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Page[OrganizationResponse]:
    service = OrganizationService(db)
    items = [
        OrganizationResponse.model_validate(organization)
        for organization in service.list(
            skip=(page - 1) * page_size,
            limit=page_size,
        )
    ]
    return create_page(
        items,
        page=page,
        page_size=page_size,
        total=service.count(),
    )


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_minimum_role(AccessRole.LEITOR)),
    ],
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    organization = OrganizationService(db).get_by_id(organization_id)
    return OrganizationResponse.model_validate(organization)
