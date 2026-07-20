from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: OrganizationCreate) -> Organization:
        organization = Organization(**payload.model_dump())
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def list(self, skip: int = 0, limit: int = 50) -> list[Organization]:
        statement = (
            select(Organization)
            .order_by(Organization.nome.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_by_id(self, organization_id: int) -> Organization | None:
        return self.db.get(Organization, organization_id)
