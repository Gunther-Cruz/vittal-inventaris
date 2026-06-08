"""create estacao trabalho table

Revision ID: c9d2e4f6a1b3
Revises: b4a8c2d1e9f0
Create Date: 2026-06-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c9d2e4f6a1b3"
down_revision = "b4a8c2d1e9f0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "estacao_trabalho",
        sa.Column("id_estacao", sa.Integer(), nullable=False),
        sa.Column("id_laboratorio", sa.Integer(), nullable=False),
        sa.Column("codigo_estacao", sa.String(length=80), nullable=False),
        sa.Column("posicao_mapa_x", sa.Integer(), nullable=True),
        sa.Column("posicao_mapa_y", sa.Integer(), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_laboratorio"], ["laboratorio.id_laboratorio"]),
        sa.PrimaryKeyConstraint("id_estacao"),
        sa.UniqueConstraint(
            "id_laboratorio",
            "codigo_estacao",
            name="uq_estacao_trabalho_laboratorio_codigo",
        ),
    )
    with op.batch_alter_table("estacao_trabalho", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_estacao_trabalho_id_laboratorio"),
            ["id_laboratorio"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("estacao_trabalho", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_estacao_trabalho_id_laboratorio"))

    op.drop_table("estacao_trabalho")
