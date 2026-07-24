"""enrich price registry items

Revision ID: 20260724_0011
Revises: 20260722_0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260724_0011"
down_revision: str | None = "20260722_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ITEMS = "price_registry_items"


def upgrade() -> None:
    op.add_column(
        ITEMS,
        sa.Column("quantidade_empenhada", sa.Numeric(18, 4), nullable=True),
    )
    op.add_column(
        ITEMS,
        sa.Column("saldo_estimado", sa.Numeric(18, 4), nullable=True),
    )
    op.add_column(
        ITEMS,
        sa.Column("limite_adesao", sa.Numeric(18, 4), nullable=True),
    )
    op.create_index(
        f"ix_{ITEMS}_quantidade_registrada",
        ITEMS,
        ["quantidade_registrada"],
    )
    op.create_index(
        f"ix_{ITEMS}_saldo_estimado",
        ITEMS,
        ["saldo_estimado"],
    )


def downgrade() -> None:
    op.drop_index(f"ix_{ITEMS}_saldo_estimado", table_name=ITEMS)
    op.drop_index(f"ix_{ITEMS}_quantidade_registrada", table_name=ITEMS)
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(ITEMS) as batch_op:
            batch_op.drop_column("limite_adesao")
            batch_op.drop_column("saldo_estimado")
            batch_op.drop_column("quantidade_empenhada")
    else:
        op.drop_column(ITEMS, "limite_adesao")
        op.drop_column(ITEMS, "saldo_estimado")
        op.drop_column(ITEMS, "quantidade_empenhada")
