"""add dashboard permission to usuario

Revision ID: 7b6f3c2a1d90
Revises: 3ede22c7df2f
Create Date: 2026-05-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "7b6f3c2a1d90"
down_revision = "3ede22c7df2f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "usuario",
        sa.Column(
            "pode_visualizar_dashboard",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("usuario", "pode_visualizar_dashboard", server_default=None)


def downgrade():
    op.drop_column("usuario", "pode_visualizar_dashboard")
