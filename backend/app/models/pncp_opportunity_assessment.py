from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PNCPOpportunityAssessmentRecord(Base):
    __tablename__ = "pncp_opportunity_assessments"
    __table_args__ = (
        UniqueConstraint(
            "contracting_id",
            "perfil",
            "perfil_versao",
            name="uq_pncp_opportunity_contracting_profile_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contracting_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_contractings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    perfil: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    perfil_versao: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    analisador_versao: Mapped[str] = mapped_column(
        String(30), nullable=False, default="legacy-unknown", index=True
    )
    ultima_execucao_id: Mapped[int | None] = mapped_column(
        ForeignKey("pncp_processing_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    classificacao: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pontuacao: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    termos_encontrados: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    evidencias: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    adequacao_perfil: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    pontuacao_adequacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requisitos_atendidos: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    requisitos_nao_atendidos: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    requisitos_nao_comprovados: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    dados_estruturados: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    classificado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contracting = relationship(
        "PNCPContractingRecord", back_populates="opportunity_assessments"
    )
    ultima_execucao = relationship("PNCPProcessingRunRecord")
    historicos = relationship(
        "PNCPOpportunityAssessmentHistoryRecord",
        back_populates="assessment",
        passive_deletes=True,
    )
