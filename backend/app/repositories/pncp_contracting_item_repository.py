from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pncp_contracting_item import PNCPContractingItemRecord
from app.schemas.pncp_items import PNCPContractingItemInput


class PNCPContractingItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(
        self, contracting_id: int, numero_item: int
    ) -> PNCPContractingItemRecord | None:
        return self.db.scalar(
            select(PNCPContractingItemRecord).where(
                PNCPContractingItemRecord.contracting_id == contracting_id,
                PNCPContractingItemRecord.numero_item == numero_item,
            )
        )

    def upsert(
        self, payload: PNCPContractingItemInput
    ) -> tuple[PNCPContractingItemRecord, bool]:
        record = self.get(payload.contracting_id, payload.numero_item)
        created = record is None
        data = payload.model_dump()
        if record is None:
            record = PNCPContractingItemRecord(**data)
            self.db.add(record)
        else:
            for field, value in data.items():
                setattr(record, field, value)
        self.db.flush()
        return record, created
