"""create laboratorio table

Revision ID: b4a8c2d1e9f0
Revises: 7b6f3c2a1d90
Create Date: 2026-06-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b4a8c2d1e9f0"
down_revision = "7b6f3c2a1d90"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "laboratorio",
        sa.Column("id_laboratorio", sa.Integer(), nullable=False),
        sa.Column("codigo_laboratorio", sa.String(length=80), nullable=False),
        sa.Column("nome_laboratorio", sa.String(length=160), nullable=False),
        sa.Column("pavilhao", sa.String(length=80), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id_laboratorio"),
    )
    with op.batch_alter_table("laboratorio", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_laboratorio_codigo_laboratorio"), ["codigo_laboratorio"], unique=True)


def downgrade():
    with op.batch_alter_table("laboratorio", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_laboratorio_codigo_laboratorio"))

    op.drop_table("laboratorio")
