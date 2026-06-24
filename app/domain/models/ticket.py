from datetime import datetime, timezone

from app.domain.enums import TicketScope, TicketStatus
from app.extensions import db


class Ticket(db.Model):
    """Single help request concept, contextualized by laboratory, workstation, or asset."""

    __tablename__ = "chamado"

    id = db.Column("id_chamado", db.Integer, primary_key=True)
    protocol = db.Column("protocolo", db.String(20), nullable=False, unique=True, index=True)
    scope = db.Column(
        "escopo",
        db.Enum(TicketScope, name="escopo_chamado", native_enum=False, length=40),
        nullable=False,
        index=True,
    )
    status = db.Column(
        "status",
        db.Enum(TicketStatus, name="status_chamado", native_enum=False, length=40),
        nullable=False,
        default=TicketStatus.ABERTO,
        index=True,
    )
    requester_name = db.Column("nome_solicitante", db.String(160), nullable=False)
    requester_email = db.Column("email_solicitante", db.String(255), nullable=False, index=True)
    description = db.Column("descricao", db.Text, nullable=False)
    laboratory_id = db.Column(
        "id_laboratorio",
        db.Integer,
        db.ForeignKey("laboratorio.id_laboratorio"),
        nullable=True,
        index=True,
    )
    workstation_id = db.Column(
        "id_estacao",
        db.Integer,
        db.ForeignKey("estacao_trabalho.id_estacao"),
        nullable=True,
        index=True,
    )
    computer_case_id = db.Column(
        "id_gabinete",
        db.Integer,
        db.ForeignKey("gabinete.id_gabinete"),
        nullable=True,
        index=True,
    )
    monitor_id = db.Column(
        "id_monitor",
        db.Integer,
        db.ForeignKey("monitor.id_monitor"),
        nullable=True,
        index=True,
    )
    created_by_user_id = db.Column(
        "id_usuario_criador",
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=True,
        index=True,
    )
    assigned_to_user_id = db.Column(
        "id_usuario_responsavel",
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=True,
        index=True,
    )
    created_at = db.Column(
        "criado_em",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        "atualizado_em",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    closed_at = db.Column("encerrado_em", db.DateTime(timezone=True), nullable=True)

    laboratory = db.relationship("Laboratory")
    workstation = db.relationship("Workstation")
    computer_case = db.relationship("ComputerCase")
    monitor = db.relationship("Monitor")
    created_by_user = db.relationship("Usuario", foreign_keys=[created_by_user_id])
    assigned_to_user = db.relationship("Usuario", foreign_keys=[assigned_to_user_id])
    history = db.relationship(
        "TicketHistory",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketHistory.created_at.asc()",
    )

    def __repr__(self) -> str:
        return (
            f"<Ticket id={self.id!r} protocol={self.protocol!r} "
            f"scope={self.scope.value!r} status={self.status.value!r}>"
        )
