"""create pncp contractings

Revision ID: 20260720_0003
Revises: 20260720_0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0003"
down_revision: str | None = "20260720_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pncp_contractings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero_controle_pncp", sa.String(length=100), nullable=False),
        sa.Column("numero_compra", sa.String(length=100), nullable=True),
        sa.Column("ano_compra", sa.Integer(), nullable=True),
        sa.Column("processo", sa.String(length=100), nullable=True),
        sa.Column("objeto_compra", sa.Text(), nullable=False),
        sa.Column("modalidade_id", sa.Integer(), nullable=True),
        sa.Column("modalidade_nome", sa.String(length=100), nullable=True),
        sa.Column("situacao_compra_nome", sa.String(length=100), nullable=True),
        sa.Column("srp", sa.Boolean(), nullable=True),
        sa.Column("data_publicacao_pncp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valor_total_estimado", sa.Numeric(18, 4), nullable=True),
        sa.Column("valor_total_homologado", sa.Numeric(18, 4), nullable=True),
        sa.Column("orgao_cnpj", sa.String(length=14), nullable=True),
        sa.Column("orgao_razao_social", sa.String(length=255), nullable=True),
        sa.Column("unidade_nome", sa.String(length=255), nullable=True),
        sa.Column("uf", sa.String(length=2), nullable=True),
        sa.Column("municipio", sa.String(length=100), nullable=True),
        sa.Column("link_sistema_origem", sa.String(length=500), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero_controle_pncp"),
    )
    for column in (
        "numero_controle_pncp",
        "ano_compra",
        "srp",
        "data_publicacao_pncp",
        "orgao_cnpj",
        "uf",
    ):
        op.create_index(f"ix_pncp_contractings_{column}", "pncp_contractings", [column])


def downgrade() -> None:
    op.drop_table("pncp_contractings")
