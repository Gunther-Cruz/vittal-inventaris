import re
from collections.abc import Mapping

from app.domain.enums import PerfilUsuario
from app.domain.models import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.security.permissions import garantir_pode_criar_usuario, perfis_criaveis_por
from app.services.auth_service import AuthService


EMAIL_INSTITUCIONAL_RE = re.compile(r"^[A-Z0-9._%+-]+@ifrs\.edu\.br$", re.IGNORECASE)


class UsuarioService:
    """Casos de uso de gestao administrativa de usuarios persistidos."""

    def __init__(
        self,
        usuario_repository: UsuarioRepository | None = None,
        auth_service: AuthService | None = None,
    ) -> None:
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.auth_service = auth_service or AuthService(self.usuario_repository)

    def cadastrar_usuario(self, dados: Mapping[str, object], ator: Usuario | None = None) -> Usuario:
        perfil = self._normalizar_perfil(dados.get("perfil", ""))
        if ator is not None:
            garantir_pode_criar_usuario(ator, perfil)

        usuario = self._construir_usuario(dados, perfil)
        if self.usuario_repository.buscar_por_email(usuario.email) is not None:
            raise ValueError("Ja existe usuario cadastrado com este email.")

        return self.usuario_repository.salvar(usuario)

    def atualizar_usuario(self, usuario: Usuario, dados: Mapping[str, object]) -> Usuario:
        """Atualiza dados administrativos sem alterar senha ou autenticacao."""
        nome = str(dados.get("nome", "")).strip()
        email = self._normalizar_email(str(dados.get("email", "")))

        if not nome:
            raise ValueError("Nome nao pode ser vazio.")

        existente = self.usuario_repository.buscar_por_email(email)
        if existente is not None and existente.id != usuario.id:
            raise ValueError("Ja existe usuario cadastrado com este email.")

        usuario.nome = nome
        usuario.email = email
        return self.usuario_repository.commit(usuario)

    def alterar_perfil(self, usuario: Usuario, perfil: PerfilUsuario | str) -> Usuario:
        usuario.perfil = self._normalizar_perfil(perfil)
        return self.usuario_repository.commit(usuario)

    def alterar_status_usuario(self, usuario: Usuario, ativo: bool) -> Usuario:
        usuario.ativo = bool(ativo)
        return self.usuario_repository.commit(usuario)

    def definir_permissao_dashboard(self, usuario: Usuario, permitido: bool) -> Usuario:
        usuario.pode_visualizar_dashboard = bool(permitido)
        return self.usuario_repository.commit(usuario)

    def listar_usuarios(self, filtros: dict | None = None) -> list[Usuario]:
        return self.usuario_repository.listar(filtros)

    def buscar_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if usuario is None:
            raise LookupError("Usuario nao encontrado.")

        return usuario

    @staticmethod
    def perfis_criaveis_por(usuario) -> tuple[PerfilUsuario, ...]:
        return perfis_criaveis_por(usuario)

    def _construir_usuario(self, dados: Mapping[str, object], perfil: PerfilUsuario) -> Usuario:
        nome = str(dados.get("nome", "")).strip()
        email = self._normalizar_email(str(dados.get("email", "")))
        senha = str(dados.get("senha", ""))

        if not nome:
            raise ValueError("Nome nao pode ser vazio.")

        self._validar_senha(senha)

        return Usuario(
            nome=nome,
            email=email,
            senha_hash=self.auth_service.gerar_hash_senha(senha),
            perfil=perfil,
        )

    @staticmethod
    def _normalizar_email(email: str) -> str:
        email_normalizado = email.strip().lower()
        if not EMAIL_INSTITUCIONAL_RE.match(email_normalizado):
            raise ValueError("Email institucional invalido.")

        return email_normalizado

    @staticmethod
    def _normalizar_perfil(perfil: PerfilUsuario | str) -> PerfilUsuario:
        if isinstance(perfil, PerfilUsuario):
            return perfil

        try:
            return PerfilUsuario[str(perfil).upper()]
        except KeyError as exc:
            raise ValueError("Perfil de usuario invalido.") from exc

    @staticmethod
    def _validar_senha(senha: str) -> None:
        if not senha or len(senha) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres.")
