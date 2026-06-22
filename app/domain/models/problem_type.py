from app.domain.enums import ProblemScope
from app.extensions import db


class ProblemType(db.Model):
    """Technical maintenance classification used by future triage and service orders."""

    __tablename__ = "tipo_problema"

    id = db.Column("id_tipo_problema", db.Integer, primary_key=True)
    code = db.Column("codigo", db.Integer, nullable=False, unique=True, index=True)
    name = db.Column("nome", db.String(160), nullable=False)
    description = db.Column("descricao", db.Text, nullable=True)
    scope = db.Column(
        "escopo",
        db.Enum(ProblemScope, name="escopo_tipo_problema", native_enum=False, length=40),
        nullable=False,
        index=True,
    )
    active = db.Column("ativo", db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column("criado_em", db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        "atualizado_em",
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<ProblemType id={self.id!r} code={self.code!r} "
            f"scope={self.scope!r} active={self.active!r}>"
        )
