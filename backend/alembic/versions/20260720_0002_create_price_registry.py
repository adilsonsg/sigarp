"""create price registry tables

Revision ID: 20260720_0002
Revises: 20260720_0001
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0002"
down_revision: str | None = "20260720_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cnpj", sa.String(length=14), nullable=True),
        sa.Column("razao_social", sa.String(length=255), nullable=False),
        sa.Column("nome_fantasia", sa.String(length=255), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cnpj", name="uq_suppliers_cnpj"),
    )
    op.create_index("ix_suppliers_cnpj", "suppliers", ["cnpj"])
    op.create_index("ix_suppliers_razao_social", "suppliers", ["razao_social"])

    op.create_table(
        "price_registry_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("numero_controle_pncp", sa.String(length=100), nullable=False),
        sa.Column("numero_ata", sa.String(length=100), nullable=True),
        sa.Column("numero_processo", sa.String(length=100), nullable=True),
        sa.Column("objeto", sa.Text(), nullable=False),
        sa.Column("vigencia_inicio", sa.Date(), nullable=True),
        sa.Column("vigencia_fim", sa.Date(), nullable=True),
        sa.Column("situacao", sa.String(length=50), nullable=True),
        sa.Column("orgao_gerenciador_id", sa.Integer(), nullable=False),
        sa.Column("url_pncp", sa.String(length=500), nullable=True),
        sa.Column("dados_fonte", sa.JSON(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["orgao_gerenciador_id"], ["organizations.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "numero_controle_pncp", name="uq_price_registry_records_pncp"
        ),
    )
    for name, column in (
        ("ix_price_registry_records_numero_controle_pncp", "numero_controle_pncp"),
        ("ix_price_registry_records_numero_ata", "numero_ata"),
        ("ix_price_registry_records_vigencia_inicio", "vigencia_inicio"),
        ("ix_price_registry_records_vigencia_fim", "vigencia_fim"),
        ("ix_price_registry_records_situacao", "situacao"),
        ("ix_price_registry_records_orgao_gerenciador_id", "orgao_gerenciador_id"),
    ):
        op.create_index(name, "price_registry_records", [column])

    op.create_table(
        "price_registry_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ata_id", sa.Integer(), nullable=False),
        sa.Column("fornecedor_id", sa.Integer(), nullable=True),
        sa.Column("numero_item", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("fabricante", sa.String(length=255), nullable=True),
        sa.Column("marca", sa.String(length=255), nullable=True),
        sa.Column("modelo", sa.String(length=255), nullable=True),
        sa.Column("unidade_medida", sa.String(length=50), nullable=True),
        sa.Column("quantidade_registrada", sa.Numeric(18, 4), nullable=True),
        sa.Column("valor_unitario", sa.Numeric(18, 4), nullable=True),
        sa.Column("dados_fonte", sa.JSON(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ata_id"], ["price_registry_records.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["fornecedor_id"], ["suppliers.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ata_id", "numero_item", name="uq_price_registry_items_ata_numero"
        ),
    )
    for name, column in (
        ("ix_price_registry_items_ata_id", "ata_id"),
        ("ix_price_registry_items_fornecedor_id", "fornecedor_id"),
        ("ix_price_registry_items_fabricante", "fabricante"),
        ("ix_price_registry_items_marca", "marca"),
        ("ix_price_registry_items_modelo", "modelo"),
    ):
        op.create_index(name, "price_registry_items", [column])


def downgrade() -> None:
    for name in (
        "ix_price_registry_items_modelo",
        "ix_price_registry_items_marca",
        "ix_price_registry_items_fabricante",
        "ix_price_registry_items_fornecedor_id",
        "ix_price_registry_items_ata_id",
    ):
        op.drop_index(name, table_name="price_registry_items")
    op.drop_table("price_registry_items")

    for name in (
        "ix_price_registry_records_orgao_gerenciador_id",
        "ix_price_registry_records_situacao",
        "ix_price_registry_records_vigencia_fim",
        "ix_price_registry_records_vigencia_inicio",
        "ix_price_registry_records_numero_ata",
        "ix_price_registry_records_numero_controle_pncp",
    ):
        op.drop_index(name, table_name="price_registry_records")
    op.drop_table("price_registry_records")

    op.drop_index("ix_suppliers_razao_social", table_name="suppliers")
    op.drop_index("ix_suppliers_cnpj", table_name="suppliers")
    op.drop_table("suppliers")
