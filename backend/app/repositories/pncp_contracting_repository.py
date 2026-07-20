from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pncp_contracting import PNCPContractingRecord
from app.schemas.pncp_sync import PNCPContractingInput


class PNCPContractingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_control_number(
        self, control_number: str
    ) -> PNCPContractingRecord | None:
        return self.db.scalar(
            select(PNCPContractingRecord).where(
                PNCPContractingRecord.numero_controle_pncp == control_number
            )
        )

    def upsert(
        self, payload: PNCPContractingInput
    ) -> tuple[PNCPContractingRecord, bool]:
        record = self.get_by_control_number(payload.numero_controle_pncp)
        created = record is None
        data = payload.model_dump()

        if record is None:
            record = PNCPContractingRecord(**data)
            self.db.add(record)
        else:
            for field, value in data.items():
                setattr(record, field, value)

        self.db.flush()
        return record, created
