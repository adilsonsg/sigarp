"""create PNCP processing runs and assessment audit trail

Revision ID: 20260722_0009
Revises: 20260722_0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260722_0009"
down_revision: str | None = "20260722_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ASSESSMENTS = "pncp_opportunity_assessments"
DOCUMENTS = "pncp_contracting_documents"
RUNS = "pncp_processing_runs"
HISTORY = "pncp_opportunity_assessment_history"
LEGACY_ANALYZER_VERSION = "legacy-unknown"
LEGACY_EXTRACTOR_VERSION = "legacy-unknown"


def upgrade() -> None:
    op.create_table(
        RUNS,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("perfil", sa.String(length=50), nullable=True),
        sa.Column("perfil_versao", sa.String(length=30), nullable=True),
        sa.Column("analisador_versao", sa.String(length=30), nullable=True),
        sa.Column("parametros", sa.JSON(), nullable=True),
        sa.Column("estatisticas", sa.JSON(), nullable=True),
        sa.Column("erro", sa.Text(), nullable=True),
        sa.Column(
            "iniciado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("concluido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in [
        "tipo",
        "status",
        "perfil",
        "perfil_versao",
        "analisador_versao",
    ]:
        op.create_index(f"ix_{RUNS}_{column}", RUNS, [column])

    analyzer_column = sa.Column(
        "analisador_versao",
        sa.String(length=30),
        nullable=False,
        server_default=LEGACY_ANALYZER_VERSION,
    )
    run_column = sa.Column("ultima_execucao_id", sa.Integer(), nullable=True)
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(ASSESSMENTS) as batch_op:
            batch_op.add_column(analyzer_column)
            batch_op.add_column(run_column)
            batch_op.create_foreign_key(
                "fk_pncp_assessment_last_run",
                RUNS,
                ["ultima_execucao_id"],
                ["id"],
                ondelete="SET NULL",
            )
        with op.batch_alter_table(ASSESSMENTS) as batch_op:
            batch_op.alter_column(
                "analisador_versao",
                existing_type=sa.String(length=30),
                nullable=False,
                server_default=None,
            )
    else:
        op.add_column(ASSESSMENTS, analyzer_column)
        op.add_column(ASSESSMENTS, run_column)
        op.create_foreign_key(
            "fk_pncp_assessment_last_run",
            ASSESSMENTS,
            RUNS,
            ["ultima_execucao_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.alter_column(
            ASSESSMENTS,
            "analisador_versao",
            existing_type=sa.String(length=30),
            nullable=False,
            server_default=None,
        )
    op.create_index(
        f"ix_{ASSESSMENTS}_analisador_versao",
        ASSESSMENTS,
        ["analisador_versao"],
    )
    op.create_index(
        f"ix_{ASSESSMENTS}_ultima_execucao_id",
        ASSESSMENTS,
        ["ultima_execucao_id"],
    )

    op.add_column(
        DOCUMENTS,
        sa.Column("extrator_versao", sa.String(length=30), nullable=True),
    )
    op.execute(
        sa.text(
            f"UPDATE {DOCUMENTS} "
            "SET extrator_versao = :version "
            "WHERE conteudo_analisado_em IS NOT NULL"
        ).bindparams(version=LEGACY_EXTRACTOR_VERSION)
    )
    op.create_index(
        f"ix_{DOCUMENTS}_extrator_versao",
        DOCUMENTS,
        ["extrator_versao"],
    )

    op.create_table(
        HISTORY,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("contracting_id", sa.Integer(), nullable=False),
        sa.Column("execucao_id", sa.Integer(), nullable=False),
        sa.Column("perfil", sa.String(length=50), nullable=False),
        sa.Column("perfil_versao", sa.String(length=30), nullable=False),
        sa.Column("analisador_versao", sa.String(length=30), nullable=False),
        sa.Column("classificacao", sa.String(length=50), nullable=False),
        sa.Column("pontuacao", sa.Integer(), nullable=False),
        sa.Column("adequacao_perfil", sa.String(length=50), nullable=True),
        sa.Column("pontuacao_adequacao", sa.Integer(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("classificado_em", sa.DateTime(timezone=True), nullable=False),
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
            ["contracting_id"],
            ["pncp_contractings.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["execucao_id"],
            [f"{RUNS}.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "execucao_id",
            "contracting_id",
            "perfil",
            "perfil_versao",
            name="uq_pncp_assessment_history_run_contracting_profile",
        ),
    )
    for column in [
        "assessment_id",
        "contracting_id",
        "execucao_id",
        "perfil",
        "perfil_versao",
        "analisador_versao",
        "classificacao",
        "adequacao_perfil",
    ]:
        op.create_index(f"ix_{HISTORY}_{column}", HISTORY, [column])


def downgrade() -> None:
    op.drop_table(HISTORY)
    op.drop_index(f"ix_{DOCUMENTS}_extrator_versao", table_name=DOCUMENTS)
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(DOCUMENTS) as batch_op:
            batch_op.drop_column("extrator_versao")
    else:
        op.drop_column(DOCUMENTS, "extrator_versao")
    op.drop_index(f"ix_{ASSESSMENTS}_ultima_execucao_id", table_name=ASSESSMENTS)
    op.drop_index(f"ix_{ASSESSMENTS}_analisador_versao", table_name=ASSESSMENTS)
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(ASSESSMENTS) as batch_op:
            batch_op.drop_constraint("fk_pncp_assessment_last_run", type_="foreignkey")
            batch_op.drop_column("ultima_execucao_id")
            batch_op.drop_column("analisador_versao")
    else:
        op.drop_constraint(
            "fk_pncp_assessment_last_run",
            ASSESSMENTS,
            type_="foreignkey",
        )
        op.drop_column(ASSESSMENTS, "ultima_execucao_id")
        op.drop_column(ASSESSMENTS, "analisador_versao")
    op.drop_table(RUNS)
