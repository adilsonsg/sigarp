from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter(prefix="/orgaos", tags=["Órgãos"])

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    try:
        obj = OrganizationRepository(db).create(payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um órgão cadastrado com este CNPJ.") from exc
    return OrganizationResponse.model_validate(obj)

@router.get("", response_model=list[OrganizationResponse])
def list_organizations(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return [OrganizationResponse.model_validate(x) for x in OrganizationRepository(db).list(skip, limit)]

@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    obj = OrganizationRepository(db).get_by_id(organization_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Órgão não encontrado.")
    return OrganizationResponse.model_validate(obj)
