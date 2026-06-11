from datetime import datetime, timezone

from app.extensions import db


class ComputerCaseAllocation(db.Model):
    """Historical allocation of a computer case to a workstation."""

    __tablename__ = "alocacao_gabinete_estacao"

    id = db.Column("id_alocacao_gabinete", db.Integer, primary_key=True)
    computer_case_id = db.Column(
        "id_gabinete",
        db.Integer,
        db.ForeignKey("gabinete.id_gabinete"),
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

    computer_case = db.relationship("ComputerCase", back_populates="allocations")
    workstation = db.relationship("Workstation", back_populates="computer_case_allocations")
    technician = db.relationship("Usuario")

    def __repr__(self) -> str:
        return (
            f"<ComputerCaseAllocation id={self.id!r} computer_case_id={self.computer_case_id!r} "
            f"workstation_id={self.workstation_id!r} end_at={self.end_at!r}>"
        )
