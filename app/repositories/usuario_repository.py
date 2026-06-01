from app.domain.models import Usuario
from app.extensions import db


class UsuarioRepository:
    """Acesso persistente a usuarios do sistema."""

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        return db.session.get(Usuario, usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return Usuario.query.filter_by(email=email.strip().lower()).first()

    def listar(self, filtros: dict | None = None) -> list[Usuario]:
        query = Usuario.query.order_by(Usuario.nome.asc())
        filtros = filtros or {}

        perfil = filtros.get("perfil")
        if perfil:
            query = query.filter_by(perfil=perfil)

        ativo = filtros.get("ativo")
        if ativo is not None:
            query = query.filter_by(ativo=ativo)

        return list(query.all())

    def salvar(self, usuario: Usuario) -> Usuario:
        db.session.add(usuario)
        return self.commit(usuario)

    def commit(self, usuario: Usuario | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return usuario
