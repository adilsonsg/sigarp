"""version opportunity assessments for neutral technical profiles

Revision ID: 20260722_0008
Revises: 20260721_0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260722_0008"
down_revision: str | None = "20260721_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE = "pncp_opportunity_assessments"
OLD_CONSTRAINT = "uq_pncp_opportunity_contracting_profile"
NEW_CONSTRAINT = "uq_pncp_opportunity_contracting_profile_version"
VERSION_INDEX = "ix_pncp_opportunity_assessments_perfil_versao"
LEGACY_VERSION = "legacy-alpha5"


def upgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(TABLE) as batch_op:
            batch_op.add_column(
                sa.Column(
                    "perfil_versao",
                    sa.String(length=30),
                    nullable=False,
                    server_default=LEGACY_VERSION,
                )
            )
            batch_op.drop_constraint(OLD_CONSTRAINT, type_="unique")
            batch_op.create_unique_constraint(
                NEW_CONSTRAINT,
                ["contracting_id", "perfil", "perfil_versao"],
            )
        with op.batch_alter_table(TABLE) as batch_op:
            batch_op.alter_column(
                "perfil_versao",
                existing_type=sa.String(length=30),
                nullable=False,
                server_default=None,
            )
        op.create_index(VERSION_INDEX, TABLE, ["perfil_versao"])
        return

    op.add_column(
        TABLE,
        sa.Column(
            "perfil_versao",
            sa.String(length=30),
            nullable=True,
            server_default=LEGACY_VERSION,
        ),
    )
    op.execute(
        sa.text(
            f"UPDATE {TABLE} SET perfil_versao = :version "
            "WHERE perfil_versao IS NULL"
        ).bindparams(version=LEGACY_VERSION)
    )
    op.alter_column(
        TABLE,
        "perfil_versao",
        existing_type=sa.String(length=30),
        nullable=False,
        server_default=None,
    )

    op.drop_constraint(OLD_CONSTRAINT, TABLE, type_="unique")
    op.create_unique_constraint(
        NEW_CONSTRAINT,
        TABLE,
        ["contracting_id", "perfil", "perfil_versao"],
    )
    op.create_index(VERSION_INDEX, TABLE, ["perfil_versao"])


def downgrade() -> None:
    op.execute(
        sa.text(
            f"DELETE FROM {TABLE} WHERE id NOT IN ("
            f"SELECT MAX(id) FROM {TABLE} GROUP BY contracting_id, perfil)"
        )
    )
    op.drop_index(VERSION_INDEX, table_name=TABLE)
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(TABLE) as batch_op:
            batch_op.drop_constraint(NEW_CONSTRAINT, type_="unique")
            batch_op.create_unique_constraint(
                OLD_CONSTRAINT,
                ["contracting_id", "perfil"],
            )
            batch_op.drop_column("perfil_versao")
    else:
        op.drop_constraint(NEW_CONSTRAINT, TABLE, type_="unique")
        op.create_unique_constraint(
            OLD_CONSTRAINT,
            TABLE,
            ["contracting_id", "perfil"],
        )
        op.drop_column(TABLE, "perfil_versao")
