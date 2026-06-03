from app.extensions import db


class Laboratory(db.Model):
    """Physical institutional laboratory managed by the inventory module."""

    __tablename__ = "laboratorio"

    id = db.Column("id_laboratorio", db.Integer, primary_key=True)
    code = db.Column("codigo_laboratorio", db.String(80), nullable=False, unique=True, index=True)
    name = db.Column("nome_laboratorio", db.String(160), nullable=False)
    pavilion = db.Column("pavilhao", db.String(80), nullable=False)
    active = db.Column("ativo", db.Boolean, nullable=False, default=True)
    notes = db.Column("observacao", db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Laboratory id={self.id!r} code={self.code!r} active={self.active!r}>"
