from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PNCPProcessingRunRecord(Base):
    __tablename__ = "pncp_processing_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    perfil: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    perfil_versao: Mapped[str | None] = mapped_column(
        String(30), nullable=True, index=True
    )
    analisador_versao: Mapped[str | None] = mapped_column(
        String(30), nullable=True, index=True
    )
    parametros: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    estatisticas: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    erro: Mapped[str | None] = mapped_column(Text, nullable=True)
    iniciado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    concluido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    historicos = relationship(
        "PNCPOpportunityAssessmentHistoryRecord",
        back_populates="execucao",
        passive_deletes=True,
    )


class PNCPOpportunityAssessmentHistoryRecord(Base):
    __tablename__ = "pncp_opportunity_assessment_history"
    __table_args__ = (
        UniqueConstraint(
            "execucao_id",
            "contracting_id",
            "perfil",
            "perfil_versao",
            name="uq_pncp_assessment_history_run_contracting_profile",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_opportunity_assessments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    contracting_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_contractings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    execucao_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_processing_runs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    perfil: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    perfil_versao: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    analisador_versao: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )
    classificacao: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pontuacao: Mapped[int] = mapped_column(Integer, nullable=False)
    adequacao_perfil: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    pontuacao_adequacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    classificado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    execucao = relationship("PNCPProcessingRunRecord", back_populates="historicos")
    assessment = relationship(
        "PNCPOpportunityAssessmentRecord", back_populates="historicos"
    )
