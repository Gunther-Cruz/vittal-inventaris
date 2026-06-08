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
    active = db.Column("ativa", db.Boolean, nullable=False, default=True)
    notes = db.Column("observacao", db.Text, nullable=True)

    laboratory = db.relationship("Laboratory", back_populates="workstations")

    def __repr__(self) -> str:
        return (
            f"<Workstation id={self.id!r} laboratory_id={self.laboratory_id!r} "
            f"code={self.code!r} active={self.active!r}>"
        )
