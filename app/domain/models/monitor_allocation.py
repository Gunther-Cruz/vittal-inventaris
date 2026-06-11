from datetime import datetime, timezone

from app.extensions import db


class MonitorAllocation(db.Model):
    """Historical allocation of a monitor to a workstation."""

    __tablename__ = "alocacao_monitor_estacao"

    id = db.Column("id_alocacao_monitor", db.Integer, primary_key=True)
    monitor_id = db.Column(
        "id_monitor",
        db.Integer,
        db.ForeignKey("monitor.id_monitor"),
        nullable=False,
        index=True,
    )
    workstation_id = db.Column(
        "id_estacao",
        db.Integer,
        db.ForeignKey("estacao_trabalho.id_estacao"),
        nullable=False,
        index=True,
    )
    technician_id = db.Column(
        "id_tecnico_responsavel",
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False,
        index=True,
    )
    start_at = db.Column(
        "data_inicio",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    end_at = db.Column("data_fim", db.DateTime(timezone=True), nullable=True, index=True)
    movement_reason = db.Column("motivo_movimentacao", db.String(255), nullable=True)
    notes = db.Column("observacao", db.Text, nullable=True)

    monitor = db.relationship("Monitor", back_populates="allocations")
    workstation = db.relationship("Workstation", back_populates="monitor_allocations")
    technician = db.relationship("Usuario")

    def __repr__(self) -> str:
        return (
            f"<MonitorAllocation id={self.id!r} monitor_id={self.monitor_id!r} "
            f"workstation_id={self.workstation_id!r} end_at={self.end_at!r}>"
        )
