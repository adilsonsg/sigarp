from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
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


class PNCPContractingItemRecord(Base):
    __tablename__ = "pncp_contracting_items"
    __table_args__ = (
        UniqueConstraint(
            "contracting_id", "numero_item", name="uq_pncp_item_contracting_numero"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contracting_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_contractings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    numero_item: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    material_ou_servico: Mapped[str | None] = mapped_column(String(1), nullable=True)
    material_ou_servico_nome: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    unidade_medida: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_unitario_estimado: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    situacao_item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    situacao_item_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    criterio_julgamento_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    criterio_julgamento_nome: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    tem_resultado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    orcamento_sigiloso: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    informacao_complementar: Mapped[str | None] = mapped_column(Text, nullable=True)
    catalogo_codigo_item: Mapped[str | None] = mapped_column(String(100), nullable=True)
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

    contracting = relationship("PNCPContractingRecord", back_populates="items")
