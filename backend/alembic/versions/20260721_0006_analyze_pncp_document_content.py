"""analyze PNCP document content

Revision ID: 20260721_0006
Revises: 20260721_0005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_0006"
down_revision: str | None = "20260721_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    columns = [
        sa.Column("nome_arquivo", sa.Text(), nullable=True),
        sa.Column("conteudo_tipo", sa.String(length=255), nullable=True),
        sa.Column("conteudo_tamanho", sa.BigInteger(), nullable=True),
        sa.Column("conteudo_sha256", sa.String(length=64), nullable=True),
        sa.Column("texto_extraido", sa.Text(), nullable=True),
        sa.Column("texto_caracteres", sa.Integer(), nullable=True),
        sa.Column("paginas_extraidas", sa.Integer(), nullable=True),
        sa.Column("extracao_status", sa.String(length=50), nullable=True),
        sa.Column("extracao_erro", sa.Text(), nullable=True),
        sa.Column(
            "conteudo_analisado_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    ]
    for column in columns:
        op.add_column("pncp_contracting_documents", column)

    op.create_index(
        "ix_pncp_contracting_documents_extracao_status",
        "pncp_contracting_documents",
        ["extracao_status"],
    )
    op.create_index(
        "ix_pncp_contracting_documents_conteudo_analisado_em",
        "pncp_contracting_documents",
        ["conteudo_analisado_em"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_pncp_contracting_documents_conteudo_analisado_em",
        table_name="pncp_contracting_documents",
    )
    op.drop_index(
        "ix_pncp_contracting_documents_extracao_status",
        table_name="pncp_contracting_documents",
    )
    for column in [
        "conteudo_analisado_em",
        "extracao_erro",
        "extracao_status",
        "paginas_extraidas",
        "texto_caracteres",
        "texto_extraido",
        "conteudo_sha256",
        "conteudo_tamanho",
        "conteudo_tipo",
        "nome_arquivo",
    ]:
        op.drop_column("pncp_contracting_documents", column)
