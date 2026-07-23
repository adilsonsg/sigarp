from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ResourceNotFoundError
from app.models.organization import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrganizationCreate


class OrganizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = OrganizationRepository(db)

    def create(self, payload: OrganizationCreate) -> Organization:
        try:
            return self.repository.create(payload)
        except IntegrityError as exception:
            self.db.rollback()
            raise ConflictError(
                "Já existe um órgão cadastrado com este CNPJ."
            ) from exception

    def list(self, skip: int = 0, limit: int = 50) -> list[Organization]:
        return self.repository.list(skip=skip, limit=limit)

    def count(self) -> int:
        return self.repository.count()

    def get_by_id(self, organization_id: int) -> Organization:
        organization = self.repository.get_by_id(organization_id)
        if organization is None:
            raise ResourceNotFoundError("Órgão não encontrado.")
        return organization
