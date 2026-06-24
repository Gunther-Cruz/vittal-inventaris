"""create ticket tables

Revision ID: b9d1e3f5a7c2
Revises: a8c4e2f1b7d9
Create Date: 2026-06-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b9d1e3f5a7c2"
down_revision = "a8c4e2f1b7d9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chamado",
        sa.Column("id_chamado", sa.Integer(), nullable=False),
        sa.Column("protocolo", sa.String(length=20), nullable=False),
        sa.Column("escopo", sa.Enum("LABORATORY", "WORKSTATION", "COMPUTER_CASE", "MONITOR", name="escopo_chamado", native_enum=False, length=40), nullable=False),
        sa.Column("status", sa.Enum("ABERTO", "EM_ATENDIMENTO", "RESOLVIDO", "CANCELADO", name="status_chamado", native_enum=False, length=40), nullable=False),
        sa.Column("nome_solicitante", sa.String(length=160), nullable=False),
        sa.Column("email_solicitante", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("id_laboratorio", sa.Integer(), nullable=True),
        sa.Column("id_estacao", sa.Integer(), nullable=True),
        sa.Column("id_gabinete", sa.Integer(), nullable=True),
        sa.Column("id_monitor", sa.Integer(), nullable=True),
        sa.Column("id_usuario_criador", sa.Integer(), nullable=True),
        sa.Column("id_usuario_responsavel", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("encerrado_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["id_estacao"], ["estacao_trabalho.id_estacao"]),
        sa.ForeignKeyConstraint(["id_gabinete"], ["gabinete.id_gabinete"]),
        sa.ForeignKeyConstraint(["id_laboratorio"], ["laboratorio.id_laboratorio"]),
        sa.ForeignKeyConstraint(["id_monitor"], ["monitor.id_monitor"]),
        sa.ForeignKeyConstraint(["id_usuario_criador"], ["usuario.id"]),
        sa.ForeignKeyConstraint(["id_usuario_responsavel"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id_chamado"),
    )
    op.create_index(op.f("ix_chamado_email_solicitante"), "chamado", ["email_solicitante"], unique=False)
    op.create_index(op.f("ix_chamado_escopo"), "chamado", ["escopo"], unique=False)
    op.create_index(op.f("ix_chamado_id_estacao"), "chamado", ["id_estacao"], unique=False)
    op.create_index(op.f("ix_chamado_id_gabinete"), "chamado", ["id_gabinete"], unique=False)
    op.create_index(op.f("ix_chamado_id_laboratorio"), "chamado", ["id_laboratorio"], unique=False)
    op.create_index(op.f("ix_chamado_id_monitor"), "chamado", ["id_monitor"], unique=False)
    op.create_index(op.f("ix_chamado_id_usuario_criador"), "chamado", ["id_usuario_criador"], unique=False)
    op.create_index(op.f("ix_chamado_id_usuario_responsavel"), "chamado", ["id_usuario_responsavel"], unique=False)
    op.create_index(op.f("ix_chamado_protocolo"), "chamado", ["protocolo"], unique=True)
    op.create_index(op.f("ix_chamado_status"), "chamado", ["status"], unique=False)

    op.create_table(
        "historico_chamado",
        sa.Column("id_historico_chamado", sa.Integer(), nullable=False),
        sa.Column("id_chamado", sa.Integer(), nullable=False),
        sa.Column("tipo_evento", sa.Enum("OPENED", "ASSIGNED", "STATUS_CHANGED", "CLOSED", "CANCELED", name="tipo_evento_historico_chamado", native_enum=False, length=40), nullable=False),
        sa.Column("status_anterior", sa.Enum("ABERTO", "EM_ATENDIMENTO", "RESOLVIDO", "CANCELADO", name="status_anterior_chamado", native_enum=False, length=40), nullable=True),
        sa.Column("status_novo", sa.Enum("ABERTO", "EM_ATENDIMENTO", "RESOLVIDO", "CANCELADO", name="status_novo_chamado", native_enum=False, length=40), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("id_usuario_criador", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["id_chamado"], ["chamado.id_chamado"]),
        sa.ForeignKeyConstraint(["id_usuario_criador"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id_historico_chamado"),
    )
    op.create_index(op.f("ix_historico_chamado_id_chamado"), "historico_chamado", ["id_chamado"], unique=False)
    op.create_index(op.f("ix_historico_chamado_id_usuario_criador"), "historico_chamado", ["id_usuario_criador"], unique=False)
    op.create_index(op.f("ix_historico_chamado_tipo_evento"), "historico_chamado", ["tipo_evento"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_historico_chamado_tipo_evento"), table_name="historico_chamado")
    op.drop_index(op.f("ix_historico_chamado_id_usuario_criador"), table_name="historico_chamado")
    op.drop_index(op.f("ix_historico_chamado_id_chamado"), table_name="historico_chamado")
    op.drop_table("historico_chamado")

    op.drop_index(op.f("ix_chamado_status"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_protocolo"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_id_usuario_responsavel"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_id_usuario_criador"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_id_monitor"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_id_laboratorio"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_id_gabinete"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_id_estacao"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_escopo"), table_name="chamado")
    op.drop_index(op.f("ix_chamado_email_solicitante"), table_name="chamado")
    op.drop_table("chamado")
