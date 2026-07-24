from sqlalchemy import func, select
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

    def count(self) -> int:
        statement = select(func.count()).select_from(Organization)
        return int(self.db.scalar(statement) or 0)

    def get_by_id(self, organization_id: int) -> Organization | None:
        return self.db.get(Organization, organization_id)

    def get_by_cnpj(self, cnpj: str) -> Organization | None:
        return self.db.scalar(select(Organization).where(Organization.cnpj == cnpj))

    def upsert_pncp(
        self,
        *,
        cnpj: str,
        nome: str,
        esfera: str,
        uf: str | None = None,
        municipio: str | None = None,
    ) -> Organization:
        organization = self.get_by_cnpj(cnpj)
        if organization is None:
            organization = Organization(
                nome=nome,
                cnpj=cnpj,
                esfera=esfera,
                uf=uf,
                municipio=municipio,
            )
            self.db.add(organization)
        else:
            organization.nome = nome
            organization.esfera = esfera
            organization.uf = uf or organization.uf
            organization.municipio = municipio or organization.municipio
        self.db.flush()
        return organization
