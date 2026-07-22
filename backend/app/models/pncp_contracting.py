from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PNCPContractingRecord(Base):
    __tablename__ = "pncp_contractings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_controle_pncp: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    numero_compra: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ano_compra: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    processo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    objeto_compra: Mapped[str] = mapped_column(Text, nullable=False)
    modalidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    modalidade_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    situacao_compra_nome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    srp: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    data_publicacao_pncp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    valor_total_estimado: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    valor_total_homologado: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    orgao_cnpj: Mapped[str | None] = mapped_column(
        String(14), nullable=True, index=True
    )
    orgao_razao_social: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unidade_nome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    municipio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    link_sistema_origem: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dados_fonte: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    documentos_sincronizados_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    documentos_quantidade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    items = relationship(
        "PNCPContractingItemRecord",
        back_populates="contracting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    documents = relationship(
        "PNCPContractingDocumentRecord",
        back_populates="contracting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    opportunity_assessments = relationship(
        "PNCPOpportunityAssessmentRecord",
        back_populates="contracting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
