"""create pncp contracting items

Revision ID: 20260721_0004
Revises: 20260720_0003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_0004"
down_revision: str | None = "20260720_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pncp_contracting_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contracting_id", sa.Integer(), nullable=False),
        sa.Column("numero_item", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("material_ou_servico", sa.String(length=1), nullable=True),
        sa.Column("material_ou_servico_nome", sa.String(length=50), nullable=True),
        sa.Column("quantidade", sa.Numeric(18, 4), nullable=True),
        sa.Column("unidade_medida", sa.String(length=100), nullable=True),
        sa.Column("valor_unitario_estimado", sa.Numeric(18, 4), nullable=True),
        sa.Column("valor_total", sa.Numeric(18, 4), nullable=True),
        sa.Column("situacao_item_id", sa.Integer(), nullable=True),
        sa.Column("situacao_item_nome", sa.String(length=100), nullable=True),
        sa.Column("criterio_julgamento_id", sa.Integer(), nullable=True),
        sa.Column("criterio_julgamento_nome", sa.String(length=100), nullable=True),
        sa.Column("tem_resultado", sa.Boolean(), nullable=True),
        sa.Column("orcamento_sigiloso", sa.Boolean(), nullable=True),
        sa.Column("informacao_complementar", sa.Text(), nullable=True),
        sa.Column("catalogo_codigo_item", sa.String(length=100), nullable=True),
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
            ["contracting_id"], ["pncp_contractings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "contracting_id", "numero_item", name="uq_pncp_item_contracting_numero"
        ),
    )
    op.create_index(
        "ix_pncp_contracting_items_contracting_id",
        "pncp_contracting_items",
        ["contracting_id"],
    )
    op.create_index(
        "ix_pncp_contracting_items_numero_item",
        "pncp_contracting_items",
        ["numero_item"],
    )


def downgrade() -> None:
    op.drop_table("pncp_contracting_items")
