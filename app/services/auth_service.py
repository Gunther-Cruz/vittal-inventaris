from werkzeug.security import check_password_hash, generate_password_hash

from app.domain.enums import PerfilUsuario
from app.domain.models import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.security.permissions import garantir_pode_criar_usuario, perfis_criaveis_por


class AuthService:
    """Casos de uso de autenticacao e gestao inicial de usuarios."""

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

    def registrar_usuario(
        self,
        nome: str,
        email: str,
        senha: str,
        perfil: PerfilUsuario | str,
    ) -> Usuario:
        usuario = self.criar_usuario(nome, email, senha, perfil)
        if self.usuario_repository.buscar_por_email(usuario.email) is not None:
            raise ValueError("Ja existe usuario cadastrado com este email.")

        return self.usuario_repository.salvar(usuario)

    def criar_usuario_por_coordenador(
        self,
        coordenador: Usuario,
        nome: str,
        email: str,
        senha: str,
        perfil: PerfilUsuario | str,
    ) -> Usuario:
        perfil_usuario = self._normalizar_perfil(perfil)
        garantir_pode_criar_usuario(coordenador, perfil_usuario)
        return self.registrar_usuario(nome, email, senha, perfil_usuario)

    @staticmethod
    def perfis_criaveis_por(usuario) -> tuple[PerfilUsuario, ...]:
        return perfis_criaveis_por(usuario)

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

    @staticmethod
    def criar_usuario(nome: str, email: str, senha: str, perfil: PerfilUsuario | str) -> Usuario:
        if not nome:
            raise ValueError("Nome nao pode ser vazio.")

        if not email:
            raise ValueError("Email nao pode ser vazio.")

        AuthService._validar_senha(senha)

        perfil_usuario = AuthService._normalizar_perfil(perfil)

        return Usuario(
            nome=nome.strip(),
            email=email.strip().lower(),
            senha_hash=AuthService.gerar_hash_senha(senha),
            perfil=perfil_usuario,
        )

    @staticmethod
    def _normalizar_perfil(perfil: PerfilUsuario | str) -> PerfilUsuario:
        if isinstance(perfil, PerfilUsuario):
            return perfil

        try:
            return PerfilUsuario[perfil.upper()]
        except KeyError as exc:
            raise ValueError("Perfil de usuario invalido.") from exc

    @staticmethod
    def _validar_senha(senha: str) -> None:
        if not senha or len(senha) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres.")
