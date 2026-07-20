from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate

class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: OrganizationCreate) -> Organization:
        obj = Organization(**payload.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self, skip: int = 0, limit: int = 50) -> list[Organization]:
        stmt = select(Organization).order_by(Organization.nome.asc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, organization_id: int) -> Organization | None:
        return self.db.get(Organization, organization_id)
