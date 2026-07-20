"""create organizations table"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = "20260720_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("sigla", sa.String(length=50), nullable=True),
        sa.Column("cnpj", sa.String(length=14), nullable=True),
        sa.Column("esfera", sa.String(length=20), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=True),
        sa.Column("municipio", sa.String(length=100), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cnpj", name="uq_organizations_cnpj"),
    )
    op.create_index("ix_organizations_nome", "organizations", ["nome"], unique=False)
    op.create_index("ix_organizations_sigla", "organizations", ["sigla"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_organizations_sigla", table_name="organizations")
    op.drop_index("ix_organizations_nome", table_name="organizations")
    op.drop_table("organizations")
