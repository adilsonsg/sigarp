"""create access review controls

Revision ID: 20260722_0010
Revises: 20260722_0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260722_0010"
down_revision: str | None = "20260722_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ASSESSMENTS = "pncp_opportunity_assessments"
REVIEWS = "pncp_opportunity_reviews"


def upgrade() -> None:
    op.add_column(
        ASSESSMENTS,
        sa.Column("revisao_status", sa.String(length=40), nullable=True),
    )
    op.add_column(
        ASSESSMENTS,
        sa.Column("revisado_por", sa.String(length=150), nullable=True),
    )
    op.add_column(
        ASSESSMENTS,
        sa.Column("revisado_em", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        f"ix_{ASSESSMENTS}_revisao_status",
        ASSESSMENTS,
        ["revisao_status"],
    )
    op.create_index(
        f"ix_{ASSESSMENTS}_revisado_por",
        ASSESSMENTS,
        ["revisado_por"],
    )

    op.create_table(
        REVIEWS,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("execucao_id", sa.Integer(), nullable=True),
        sa.Column("actor_subject", sa.String(length=150), nullable=False),
        sa.Column("actor_name", sa.String(length=200), nullable=False),
        sa.Column("actor_role", sa.String(length=30), nullable=False),
        sa.Column("decisao", sa.String(length=40), nullable=False),
        sa.Column("justificativa", sa.Text(), nullable=False),
        sa.Column("resultado_avaliado", sa.JSON(), nullable=False),
        sa.Column("valor_anterior", sa.JSON(), nullable=False),
        sa.Column("valor_novo", sa.JSON(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            [f"{ASSESSMENTS}.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["execucao_id"],
            ["pncp_processing_runs.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in [
        "assessment_id",
        "execucao_id",
        "actor_subject",
        "actor_role",
        "decisao",
    ]:
        op.create_index(f"ix_{REVIEWS}_{column}", REVIEWS, [column])


def downgrade() -> None:
    op.drop_table(REVIEWS)
    op.drop_index(f"ix_{ASSESSMENTS}_revisado_por", table_name=ASSESSMENTS)
    op.drop_index(f"ix_{ASSESSMENTS}_revisao_status", table_name=ASSESSMENTS)
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(ASSESSMENTS) as batch_op:
            batch_op.drop_column("revisado_em")
            batch_op.drop_column("revisado_por")
            batch_op.drop_column("revisao_status")
    else:
        op.drop_column(ASSESSMENTS, "revisado_em")
        op.drop_column(ASSESSMENTS, "revisado_por")
        op.drop_column(ASSESSMENTS, "revisao_status")
