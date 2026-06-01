from werkzeug.security import check_password_hash, generate_password_hash

from app.domain.models import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.security.permissions import pode_visualizar_dashboard


class AuthService:
    """Casos de uso ligados a autenticacao e autorizacao do usuario logado."""

    def __init__(self, usuario_repository: UsuarioRepository | None = None) -> None:
        self.usuario_repository = usuario_repository or UsuarioRepository()

    def autenticar(self, email: str, senha: str) -> Usuario | None:
        """Autentica usuario ativo por email e senha sem expor motivo da falha."""
        if not email or not senha:
            return None

        usuario = self.usuario_repository.buscar_por_email(email.strip().lower())
        if usuario is None or not usuario.ativo:
            return None

        if not self.verificar_senha(senha, usuario.senha_hash):
            return None

        return usuario

    def verificar_permissao_dashboard(self, usuario: Usuario) -> bool:
        """Aplica a politica centralizada de acesso ao dashboard."""
        return pode_visualizar_dashboard(usuario)

    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        if not senha:
            raise ValueError("Senha nao pode ser vazia.")

        return generate_password_hash(senha)

    @staticmethod
    def verificar_senha(senha: str, senha_hash: str) -> bool:
        if not senha or not senha_hash:
            return False

        return check_password_hash(senha_hash, senha)
