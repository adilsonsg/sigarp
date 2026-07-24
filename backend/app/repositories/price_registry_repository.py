from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.organization import Organization
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

    def upsert(
        self,
        payload: PriceRegistryRecordInput,
        *,
        replace_items: bool = True,
    ) -> PriceRegistryRecord:
        record = self.get_by_control_number(payload.numero_controle_pncp)
        record_data = payload.model_dump(exclude={"itens"})

        if record is None:
            record = PriceRegistryRecord(**record_data)
            self.db.add(record)
            self.db.flush()
        else:
            for field, value in record_data.items():
                setattr(record, field, value)
            if replace_items:
                record.itens.clear()
                self.db.flush()

        if replace_items:
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
        sphere: str | None = None,
        uf: str | None = None,
        valid_on: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PriceRegistryRecord]:
        statement = select(PriceRegistryRecord).options(
            selectinload(PriceRegistryRecord.itens)
        )

        if term:
            pattern = f"%{term.strip()}%"
            item_matches = PriceRegistryRecord.itens.any(
                or_(
                    PriceRegistryItem.descricao.ilike(pattern),
                    PriceRegistryItem.fabricante.ilike(pattern),
                    PriceRegistryItem.marca.ilike(pattern),
                    PriceRegistryItem.modelo.ilike(pattern),
                )
            )
            statement = statement.where(
                or_(
                    PriceRegistryRecord.objeto.ilike(pattern),
                    item_matches,
                )
            )

        if only_active or valid_on:
            reference_date = valid_on or date.today()
            statement = statement.where(
                PriceRegistryRecord.vigencia_inicio <= reference_date,
                PriceRegistryRecord.vigencia_fim >= reference_date,
                PriceRegistryRecord.situacao.ilike("vigente"),
            )

        if sphere or uf:
            statement = statement.join(PriceRegistryRecord.orgao_gerenciador)
            if sphere:
                statement = statement.where(
                    func.lower(Organization.esfera) == sphere.lower()
                )
            if uf:
                statement = statement.where(func.upper(Organization.uf) == uf.upper())

        statement = (
            statement.order_by(PriceRegistryRecord.vigencia_fim.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement).unique().all())

    def count(
        self,
        term: str | None = None,
        *,
        only_active: bool = False,
        sphere: str | None = None,
        uf: str | None = None,
        valid_on: date | None = None,
    ) -> int:
        return len(
            self.search(
                term,
                only_active=only_active,
                sphere=sphere,
                uf=uf,
                valid_on=valid_on,
                limit=1_000_000,
            )
        )

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
