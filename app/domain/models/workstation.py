from app.extensions import db


class Workstation(db.Model):
    """Fixed physical workstation position inside an institutional laboratory."""

    __tablename__ = "estacao_trabalho"
    __table_args__ = (
        db.UniqueConstraint(
            "id_laboratorio",
            "codigo_estacao",
            name="uq_estacao_trabalho_laboratorio_codigo",
        ),
    )

    id = db.Column("id_estacao", db.Integer, primary_key=True)
    laboratory_id = db.Column(
        "id_laboratorio",
        db.Integer,
        db.ForeignKey("laboratorio.id_laboratorio"),
        nullable=False,
        index=True,
    )
    code = db.Column("codigo_estacao", db.String(80), nullable=False)
    map_position_x = db.Column("posicao_mapa_x", db.Integer, nullable=True)
    map_position_y = db.Column("posicao_mapa_y", db.Integer, nullable=True)
    current_computer_case_id = db.Column(
        "id_gabinete_atual",
        db.Integer,
        db.ForeignKey("gabinete.id_gabinete"),
        nullable=True,
        unique=True,
        index=True,
    )
    current_monitor_id = db.Column(
        "id_monitor_atual",
        db.Integer,
        db.ForeignKey("monitor.id_monitor"),
        nullable=True,
        unique=True,
        index=True,
    )
    active = db.Column("ativa", db.Boolean, nullable=False, default=True)
    notes = db.Column("observacao", db.Text, nullable=True)

    laboratory = db.relationship("Laboratory", back_populates="workstations")
    current_computer_case = db.relationship("ComputerCase", foreign_keys=[current_computer_case_id])
    current_monitor = db.relationship("Monitor", foreign_keys=[current_monitor_id])
    computer_case_allocations = db.relationship(
        "ComputerCaseAllocation",
        back_populates="workstation",
        cascade="all, delete-orphan",
    )
    monitor_allocations = db.relationship(
        "MonitorAllocation",
        back_populates="workstation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Workstation id={self.id!r} laboratory_id={self.laboratory_id!r} "
            f"code={self.code!r} active={self.active!r}>"
        )
