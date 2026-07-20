from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PriceRegistryRecord(Base):
    __tablename__ = "price_registry_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_controle_pncp: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    numero_ata: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    numero_processo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    objeto: Mapped[str] = mapped_column(Text, nullable=False)
    vigencia_inicio: Mapped[date | None] = mapped_column(
        Date, nullable=True, index=True
    )
    vigencia_fim: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    situacao: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    orgao_gerenciador_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    url_pncp: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dados_fonte: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    orgao_gerenciador: Mapped["Organization"] = relationship()  # noqa: F821
    itens: Mapped[list["PriceRegistryItem"]] = relationship(
        back_populates="ata",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PriceRegistryItem(Base):
    __tablename__ = "price_registry_items"
    __table_args__ = (
        UniqueConstraint(
            "ata_id", "numero_item", name="uq_price_registry_items_ata_numero"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ata_id: Mapped[int] = mapped_column(
        ForeignKey("price_registry_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fornecedor_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    numero_item: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    fabricante: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    marca: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    modelo: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    unidade_medida: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantidade_registrada: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    valor_unitario: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    dados_fonte: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ata: Mapped[PriceRegistryRecord] = relationship(back_populates="itens")
    fornecedor: Mapped["Supplier | None"] = relationship(  # noqa: F821
        back_populates="itens"
    )
