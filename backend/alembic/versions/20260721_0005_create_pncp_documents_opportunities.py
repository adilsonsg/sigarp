"""create PNCP documents and opportunity assessments

Revision ID: 20260721_0005
Revises: 20260721_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_0005"
down_revision: str | None = "20260721_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "pncp_contractings",
        sa.Column(
            "documentos_sincronizados_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "pncp_contractings",
        sa.Column("documentos_quantidade", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_pncp_contractings_documentos_sincronizados_em",
        "pncp_contractings",
        ["documentos_sincronizados_em"],
    )

    op.create_table(
        "pncp_contracting_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contracting_id", sa.Integer(), nullable=False),
        sa.Column("sequencial_documento", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.Text(), nullable=True),
        sa.Column("tipo_documento_id", sa.Integer(), nullable=True),
        sa.Column("tipo_documento_nome", sa.String(length=150), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("uri", sa.Text(), nullable=True),
        sa.Column(
            "data_publicacao_pncp",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("dados_fonte", sa.JSON(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contracting_id"],
            ["pncp_contractings.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "contracting_id",
            "sequencial_documento",
            name="uq_pncp_document_contracting_sequencial",
        ),
    )
    op.create_index(
        "ix_pncp_contracting_documents_contracting_id",
        "pncp_contracting_documents",
        ["contracting_id"],
    )
    op.create_index(
        "ix_pncp_contracting_documents_data_publicacao_pncp",
        "pncp_contracting_documents",
        ["data_publicacao_pncp"],
    )

    op.create_table(
        "pncp_opportunity_assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contracting_id", sa.Integer(), nullable=False),
        sa.Column("perfil", sa.String(length=50), nullable=False),
        sa.Column("classificacao", sa.String(length=50), nullable=False),
        sa.Column("pontuacao", sa.Integer(), nullable=False),
        sa.Column("termos_encontrados", sa.JSON(), nullable=True),
        sa.Column("evidencias", sa.JSON(), nullable=True),
        sa.Column(
            "classificado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contracting_id"],
            ["pncp_contractings.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "contracting_id",
            "perfil",
            name="uq_pncp_opportunity_contracting_profile",
        ),
    )
    op.create_index(
        "ix_pncp_opportunity_assessments_contracting_id",
        "pncp_opportunity_assessments",
        ["contracting_id"],
    )
    op.create_index(
        "ix_pncp_opportunity_assessments_perfil",
        "pncp_opportunity_assessments",
        ["perfil"],
    )
    op.create_index(
        "ix_pncp_opportunity_assessments_classificacao",
        "pncp_opportunity_assessments",
        ["classificacao"],
    )


def downgrade() -> None:
    op.drop_table("pncp_opportunity_assessments")
    op.drop_table("pncp_contracting_documents")
    op.drop_index(
        "ix_pncp_contractings_documentos_sincronizados_em",
        table_name="pncp_contractings",
    )
    op.drop_column("pncp_contractings", "documentos_quantidade")
    op.drop_column("pncp_contractings", "documentos_sincronizados_em")
