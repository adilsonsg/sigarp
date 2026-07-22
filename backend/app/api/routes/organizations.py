from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.security.authentication import require_minimum_role
from app.security.models import AccessRole, AuthenticatedPrincipal
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/orgaos", tags=["Órgãos"])


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
    service = OrganizationService(db)
    organization = service.create(payload)
    return OrganizationResponse.model_validate(organization)


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_minimum_role(AccessRole.LEITOR)),
    ],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    service = OrganizationService(db)
    organizations = service.list(skip=skip, limit=limit)
    return [
        OrganizationResponse.model_validate(organization)
        for organization in organizations
    ]


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_minimum_role(AccessRole.LEITOR)),
    ],
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    service = OrganizationService(db)
    organization = service.get_by_id(organization_id)
    return OrganizationResponse.model_validate(organization)
