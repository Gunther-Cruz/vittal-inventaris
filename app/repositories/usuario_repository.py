from app.domain.models import Usuario
from app.extensions import db


class UsuarioRepository:
    """Acesso persistente a usuarios do sistema."""

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        return db.session.get(Usuario, usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return Usuario.query.filter_by(email=email.strip().lower()).first()

    def salvar(self, usuario: Usuario) -> Usuario:
        db.session.add(usuario)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return usuario
