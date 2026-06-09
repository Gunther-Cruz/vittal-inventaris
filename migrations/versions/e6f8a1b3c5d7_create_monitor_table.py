"""create monitor table

Revision ID: e6f8a1b3c5d7
Revises: d5e7f9a2b4c6
Create Date: 2026-06-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e6f8a1b3c5d7"
down_revision = "d5e7f9a2b4c6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "monitor",
        sa.Column("id_monitor", sa.Integer(), nullable=False),
        sa.Column("num_patrimonio", sa.String(length=80), nullable=False),
        sa.Column("numero_serie", sa.String(length=120), nullable=True),
        sa.Column("fabricante", sa.String(length=120), nullable=False),
        sa.Column("modelo", sa.String(length=120), nullable=False),
        sa.Column("data_compra", sa.Date(), nullable=True),
        sa.Column(
            "situacao_operacional",
            sa.Enum(
                "EM_FUNCIONAMENTO",
                "EM_MANUTENCAO",
                "DESATIVADO",
                "FUNCIONAL_DESALOCADO",
                name="situacao_operacional_ativo",
                native_enum=False,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("polegadas", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "tipo_conexao",
            sa.Enum(
                "HDMI",
                "VGA",
                "DISPLAYPORT",
                "DVI",
                "USB_C",
                "OUTRA",
                name="tipo_conexao_monitor",
                native_enum=False,
                length=40,
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id_monitor"),
    )
    op.create_index("ix_monitor_num_patrimonio", "monitor", ["num_patrimonio"], unique=True)
    op.create_index("ix_monitor_numero_serie", "monitor", ["numero_serie"], unique=True)


def downgrade():
    op.drop_index("ix_monitor_numero_serie", table_name="monitor")
    op.drop_index("ix_monitor_num_patrimonio", table_name="monitor")
    op.drop_table("monitor")
