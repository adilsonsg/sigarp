"""add projector profile suitability assessment

Revision ID: 20260721_0007
Revises: 20260721_0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260721_0007"
down_revision: str | None = "20260721_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "pncp_opportunity_assessments",
        sa.Column("adequacao_perfil", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "pncp_opportunity_assessments",
        sa.Column("pontuacao_adequacao", sa.Integer(), nullable=True),
    )
    op.add_column(
        "pncp_opportunity_assessments",
        sa.Column("requisitos_atendidos", sa.JSON(), nullable=True),
    )
    op.add_column(
        "pncp_opportunity_assessments",
        sa.Column("requisitos_nao_atendidos", sa.JSON(), nullable=True),
    )
    op.add_column(
        "pncp_opportunity_assessments",
        sa.Column("requisitos_nao_comprovados", sa.JSON(), nullable=True),
    )
    op.add_column(
        "pncp_opportunity_assessments",
        sa.Column("dados_estruturados", sa.JSON(), nullable=True),
    )
    op.create_index(
        "ix_pncp_opportunity_assessments_adequacao_perfil",
        "pncp_opportunity_assessments",
        ["adequacao_perfil"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_pncp_opportunity_assessments_adequacao_perfil",
        table_name="pncp_opportunity_assessments",
    )
    for column in [
        "dados_estruturados",
        "requisitos_nao_comprovados",
        "requisitos_nao_atendidos",
        "requisitos_atendidos",
        "pontuacao_adequacao",
        "adequacao_perfil",
    ]:
        op.drop_column("pncp_opportunity_assessments", column)
