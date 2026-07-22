from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PNCPOpportunityReviewRecord(Base):
    __tablename__ = "pncp_opportunity_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_opportunity_assessments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    execucao_id: Mapped[int | None] = mapped_column(
        ForeignKey("pncp_processing_runs.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    actor_subject: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    actor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    decisao: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    justificativa: Mapped[str] = mapped_column(Text, nullable=False)
    resultado_avaliado: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    valor_anterior: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    valor_novo: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    assessment = relationship(
        "PNCPOpportunityAssessmentRecord",
        back_populates="revisoes",
    )
