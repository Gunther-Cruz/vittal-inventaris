from datetime import datetime, timezone

from app.domain.enums import TicketHistoryEvent, TicketStatus
from app.extensions import db


class TicketHistory(db.Model):
    """Auditable event in the lifecycle of a help request."""

    __tablename__ = "historico_chamado"

    id = db.Column("id_historico_chamado", db.Integer, primary_key=True)
    ticket_id = db.Column(
        "id_chamado",
        db.Integer,
        db.ForeignKey("chamado.id_chamado"),
        nullable=False,
        index=True,
    )
    event_type = db.Column(
        "tipo_evento",
        db.Enum(TicketHistoryEvent, name="tipo_evento_historico_chamado", native_enum=False, length=40),
        nullable=False,
        index=True,
    )
    previous_status = db.Column(
        "status_anterior",
        db.Enum(TicketStatus, name="status_anterior_chamado", native_enum=False, length=40),
        nullable=True,
    )
    new_status = db.Column(
        "status_novo",
        db.Enum(TicketStatus, name="status_novo_chamado", native_enum=False, length=40),
        nullable=True,
    )
    description = db.Column("descricao", db.Text, nullable=False)
    created_by_user_id = db.Column(
        "id_usuario_criador",
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

    ticket = db.relationship("Ticket", back_populates="history")
    created_by_user = db.relationship("Usuario")

    def __repr__(self) -> str:
        return f"<TicketHistory id={self.id!r} ticket_id={self.ticket_id!r} event={self.event_type.value!r}>"
