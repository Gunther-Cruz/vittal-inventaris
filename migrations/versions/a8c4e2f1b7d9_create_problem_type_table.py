"""create problem type table

Revision ID: a8c4e2f1b7d9
Revises: f7a9c2d4e6b8
Create Date: 2026-06-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a8c4e2f1b7d9"
down_revision = "f7a9c2d4e6b8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tipo_problema",
        sa.Column("id_tipo_problema", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("escopo", sa.Enum("LABORATORY", "WORKSTATION", "COMPUTER_CASE", "MONITOR", name="escopo_tipo_problema", native_enum=False, length=40), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id_tipo_problema"),
    )
    op.create_index(op.f("ix_tipo_problema_ativo"), "tipo_problema", ["ativo"], unique=False)
    op.create_index(op.f("ix_tipo_problema_codigo"), "tipo_problema", ["codigo"], unique=True)
    op.create_index(op.f("ix_tipo_problema_escopo"), "tipo_problema", ["escopo"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_tipo_problema_escopo"), table_name="tipo_problema")
    op.drop_index(op.f("ix_tipo_problema_codigo"), table_name="tipo_problema")
    op.drop_index(op.f("ix_tipo_problema_ativo"), table_name="tipo_problema")
    op.drop_table("tipo_problema")
