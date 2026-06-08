"""create gabinete table

Revision ID: d5e7f9a2b4c6
Revises: c9d2e4f6a1b3
Create Date: 2026-06-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d5e7f9a2b4c6"
down_revision = "c9d2e4f6a1b3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "gabinete",
        sa.Column("id_gabinete", sa.Integer(), nullable=False),
        sa.Column("num_patrimonio", sa.String(length=80), nullable=False),
        sa.Column("numero_serie", sa.String(length=120), nullable=True),
        sa.Column("fabricante", sa.String(length=120), nullable=False),
        sa.Column("modelo", sa.String(length=120), nullable=False),
        sa.Column("lote", sa.String(length=120), nullable=True),
        sa.Column("data_compra", sa.Date(), nullable=True),
        sa.Column("processador_modelo", sa.String(length=160), nullable=True),
        sa.Column("processador_frequencia_ghz", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("placa_mae_modelo", sa.String(length=160), nullable=True),
        sa.Column("memoria_instalada_gb", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("memoria_tecnologia", sa.String(length=80), nullable=True),
        sa.Column("memoria_velocidade_mhz", sa.Integer(), nullable=True),
        sa.Column("memoria_slots_total", sa.Integer(), nullable=True),
        sa.Column("memoria_slots_ocupacao", sa.String(length=120), nullable=True),
        sa.Column("armazenamento_descricao", sa.String(length=255), nullable=True),
        sa.Column("fonte_descricao", sa.String(length=255), nullable=True),
        sa.Column("sistema_operacional", sa.String(length=160), nullable=True),
        sa.Column(
            "situacao_operacional",
            sa.Enum(
                "EM_FUNCIONAMENTO",
                "EM_MANUTENCAO",
                "DESATIVADO",
                "FUNCIONAL_DESALOCADO",
                name="situacao_operacional_gabinete",
                native_enum=False,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id_gabinete"),
    )
    op.create_index("ix_gabinete_num_patrimonio", "gabinete", ["num_patrimonio"], unique=True)
    op.create_index("ix_gabinete_numero_serie", "gabinete", ["numero_serie"], unique=True)


def downgrade():
    op.drop_index("ix_gabinete_numero_serie", table_name="gabinete")
    op.drop_index("ix_gabinete_num_patrimonio", table_name="gabinete")
    op.drop_table("gabinete")
