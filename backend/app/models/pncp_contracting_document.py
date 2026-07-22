from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
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


class PNCPContractingDocumentRecord(Base):
    __tablename__ = "pncp_contracting_documents"
    __table_args__ = (
        UniqueConstraint(
            "contracting_id",
            "sequencial_documento",
            name="uq_pncp_document_contracting_sequencial",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contracting_id: Mapped[int] = mapped_column(
        ForeignKey("pncp_contractings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequencial_documento: Mapped[int] = mapped_column(Integer, nullable=False)
    titulo: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_documento_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tipo_documento_nome: Mapped[str | None] = mapped_column(String(150), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_publicacao_pncp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    dados_fonte: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    nome_arquivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    conteudo_tipo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conteudo_tamanho: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    conteudo_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    texto_extraido: Mapped[str | None] = mapped_column(Text, nullable=True)
    texto_caracteres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    paginas_extraidas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracao_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    extrator_versao: Mapped[str | None] = mapped_column(
        String(30), nullable=True, index=True
    )
    extracao_erro: Mapped[str | None] = mapped_column(Text, nullable=True)
    conteudo_analisado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
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

    contracting = relationship("PNCPContractingRecord", back_populates="documents")
