from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.price_registry import PriceRegistryItem, PriceRegistryRecord
from app.models.supplier import Supplier
from app.schemas.price_registry import PriceRegistryRecordInput, SupplierInput


class PriceRegistryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_control_number(self, control_number: str) -> PriceRegistryRecord | None:
        statement = (
            select(PriceRegistryRecord)
            .options(
                selectinload(PriceRegistryRecord.itens).selectinload(
                    PriceRegistryItem.fornecedor
                )
            )
            .where(PriceRegistryRecord.numero_controle_pncp == control_number)
        )
        return self.db.scalar(statement)

    def upsert(self, payload: PriceRegistryRecordInput) -> PriceRegistryRecord:
        record = self.get_by_control_number(payload.numero_controle_pncp)
        record_data = payload.model_dump(exclude={"itens"})

        if record is None:
            record = PriceRegistryRecord(**record_data)
            self.db.add(record)
            self.db.flush()
        else:
            for field, value in record_data.items():
                setattr(record, field, value)
            record.itens.clear()
            self.db.flush()

        for item_payload in payload.itens:
            item_data = item_payload.model_dump(exclude={"fornecedor"})
            supplier = self._get_or_create_supplier(item_payload.fornecedor)
            record.itens.append(PriceRegistryItem(**item_data, fornecedor=supplier))

        self.db.commit()
        return self.get_by_control_number(payload.numero_controle_pncp)  # type: ignore[return-value]

    def search(
        self,
        term: str | None = None,
        *,
        only_active: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PriceRegistryRecord]:
        statement = select(PriceRegistryRecord).options(
            selectinload(PriceRegistryRecord.itens)
        )

        if term:
            pattern = f"%{term.strip()}%"
            statement = statement.join(PriceRegistryRecord.itens).where(
                or_(
                    PriceRegistryRecord.objeto.ilike(pattern),
                    PriceRegistryItem.descricao.ilike(pattern),
                    PriceRegistryItem.fabricante.ilike(pattern),
                    PriceRegistryItem.marca.ilike(pattern),
                    PriceRegistryItem.modelo.ilike(pattern),
                )
            )

        if only_active:
            statement = statement.where(
                or_(
                    PriceRegistryRecord.situacao.is_(None),
                    PriceRegistryRecord.situacao.ilike("vigente"),
                    PriceRegistryRecord.situacao.ilike("ativa"),
                )
            )

        statement = (
            statement.distinct()
            .order_by(PriceRegistryRecord.vigencia_fim.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement).unique().all())

    def _get_or_create_supplier(self, payload: SupplierInput | None) -> Supplier | None:
        if payload is None:
            return None

        supplier: Supplier | None = None
        if payload.cnpj:
            supplier = self.db.scalar(
                select(Supplier).where(Supplier.cnpj == payload.cnpj)
            )
        if supplier is None:
            supplier = Supplier(**payload.model_dump())
            self.db.add(supplier)
            self.db.flush()
        else:
            supplier.razao_social = payload.razao_social
            supplier.nome_fantasia = payload.nome_fantasia
        return supplier
