from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pncp_contracting_document import PNCPContractingDocumentRecord
from app.schemas.pncp_documents import PNCPContractingDocumentInput


class PNCPContractingDocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(
        self, contracting_id: int, sequencial_documento: int
    ) -> PNCPContractingDocumentRecord | None:
        return self.db.scalar(
            select(PNCPContractingDocumentRecord).where(
                PNCPContractingDocumentRecord.contracting_id == contracting_id,
                PNCPContractingDocumentRecord.sequencial_documento
                == sequencial_documento,
            )
        )

    def upsert(
        self, payload: PNCPContractingDocumentInput
    ) -> tuple[PNCPContractingDocumentRecord, bool]:
        record = self.get(payload.contracting_id, payload.sequencial_documento)
        created = record is None
        data = payload.model_dump()
        if record is None:
            record = PNCPContractingDocumentRecord(**data)
            self.db.add(record)
        else:
            for field, value in data.items():
                setattr(record, field, value)
        self.db.flush()
        return record, created
