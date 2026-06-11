"""create asset allocations

Revision ID: f7a9c2d4e6b8
Revises: e6f8a1b3c5d7
Create Date: 2026-06-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f7a9c2d4e6b8"
down_revision = "e6f8a1b3c5d7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("estacao_trabalho", sa.Column("id_gabinete_atual", sa.Integer(), nullable=True))
    op.add_column("estacao_trabalho", sa.Column("id_monitor_atual", sa.Integer(), nullable=True))
    op.create_index("ix_estacao_trabalho_id_gabinete_atual", "estacao_trabalho", ["id_gabinete_atual"], unique=True)
    op.create_index("ix_estacao_trabalho_id_monitor_atual", "estacao_trabalho", ["id_monitor_atual"], unique=True)
    op.create_foreign_key(
        "fk_estacao_trabalho_gabinete_atual",
        "estacao_trabalho",
        "gabinete",
        ["id_gabinete_atual"],
        ["id_gabinete"],
    )
    op.create_foreign_key(
        "fk_estacao_trabalho_monitor_atual",
        "estacao_trabalho",
        "monitor",
        ["id_monitor_atual"],
        ["id_monitor"],
    )

    op.execute(
        "UPDATE gabinete SET situacao_operacional = 'FUNCIONAL_DESALOCADO' "
        "WHERE situacao_operacional = 'EM_FUNCIONAMENTO'"
    )
    op.execute(
        "UPDATE monitor SET situacao_operacional = 'FUNCIONAL_DESALOCADO' "
        "WHERE situacao_operacional = 'EM_FUNCIONAMENTO'"
    )

    op.create_table(
        "alocacao_gabinete_estacao",
        sa.Column("id_alocacao_gabinete", sa.Integer(), nullable=False),
        sa.Column("id_gabinete", sa.Integer(), nullable=False),
        sa.Column("id_estacao", sa.Integer(), nullable=False),
        sa.Column("id_tecnico_responsavel", sa.Integer(), nullable=False),
        sa.Column("data_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_fim", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motivo_movimentacao", sa.String(length=255), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_estacao"], ["estacao_trabalho.id_estacao"]),
        sa.ForeignKeyConstraint(["id_gabinete"], ["gabinete.id_gabinete"]),
        sa.ForeignKeyConstraint(["id_tecnico_responsavel"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id_alocacao_gabinete"),
    )
    op.create_index("ix_alocacao_gabinete_estacao_id_estacao", "alocacao_gabinete_estacao", ["id_estacao"])
    op.create_index("ix_alocacao_gabinete_estacao_id_gabinete", "alocacao_gabinete_estacao", ["id_gabinete"])
    op.create_index(
        "ix_alocacao_gabinete_estacao_id_tecnico_responsavel",
        "alocacao_gabinete_estacao",
        ["id_tecnico_responsavel"],
    )
    op.create_index("ix_alocacao_gabinete_estacao_data_fim", "alocacao_gabinete_estacao", ["data_fim"])

    op.create_table(
        "alocacao_monitor_estacao",
        sa.Column("id_alocacao_monitor", sa.Integer(), nullable=False),
        sa.Column("id_monitor", sa.Integer(), nullable=False),
        sa.Column("id_estacao", sa.Integer(), nullable=False),
        sa.Column("id_tecnico_responsavel", sa.Integer(), nullable=False),
        sa.Column("data_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_fim", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motivo_movimentacao", sa.String(length=255), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_estacao"], ["estacao_trabalho.id_estacao"]),
        sa.ForeignKeyConstraint(["id_monitor"], ["monitor.id_monitor"]),
        sa.ForeignKeyConstraint(["id_tecnico_responsavel"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id_alocacao_monitor"),
    )
    op.create_index("ix_alocacao_monitor_estacao_id_estacao", "alocacao_monitor_estacao", ["id_estacao"])
    op.create_index("ix_alocacao_monitor_estacao_id_monitor", "alocacao_monitor_estacao", ["id_monitor"])
    op.create_index(
        "ix_alocacao_monitor_estacao_id_tecnico_responsavel",
        "alocacao_monitor_estacao",
        ["id_tecnico_responsavel"],
    )
    op.create_index("ix_alocacao_monitor_estacao_data_fim", "alocacao_monitor_estacao", ["data_fim"])


def downgrade():
    op.drop_index("ix_alocacao_monitor_estacao_data_fim", table_name="alocacao_monitor_estacao")
    op.drop_index("ix_alocacao_monitor_estacao_id_tecnico_responsavel", table_name="alocacao_monitor_estacao")
    op.drop_index("ix_alocacao_monitor_estacao_id_monitor", table_name="alocacao_monitor_estacao")
    op.drop_index("ix_alocacao_monitor_estacao_id_estacao", table_name="alocacao_monitor_estacao")
    op.drop_table("alocacao_monitor_estacao")

    op.drop_index("ix_alocacao_gabinete_estacao_data_fim", table_name="alocacao_gabinete_estacao")
    op.drop_index("ix_alocacao_gabinete_estacao_id_tecnico_responsavel", table_name="alocacao_gabinete_estacao")
    op.drop_index("ix_alocacao_gabinete_estacao_id_gabinete", table_name="alocacao_gabinete_estacao")
    op.drop_index("ix_alocacao_gabinete_estacao_id_estacao", table_name="alocacao_gabinete_estacao")
    op.drop_table("alocacao_gabinete_estacao")

    op.drop_constraint("fk_estacao_trabalho_monitor_atual", "estacao_trabalho", type_="foreignkey")
    op.drop_constraint("fk_estacao_trabalho_gabinete_atual", "estacao_trabalho", type_="foreignkey")
    op.drop_index("ix_estacao_trabalho_id_monitor_atual", table_name="estacao_trabalho")
    op.drop_index("ix_estacao_trabalho_id_gabinete_atual", table_name="estacao_trabalho")
    op.drop_column("estacao_trabalho", "id_monitor_atual")
    op.drop_column("estacao_trabalho", "id_gabinete_atual")
