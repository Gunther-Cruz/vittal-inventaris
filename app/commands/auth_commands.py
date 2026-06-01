import click
from flask.cli import AppGroup

from app.domain.enums import PerfilUsuario
from app.repositories.usuario_repository import UsuarioRepository
from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService

auth_cli = AppGroup("auth")
COORDENADOR_INICIAL_NOME = "Coordenador Inicial"
COORDENADOR_INICIAL_EMAIL = "coordenador.inicial@ifrs.edu.br"
COORDENADOR_INICIAL_SENHA = "SenhaCoordenador123!"


@auth_cli.command("criar-usuario")
@click.option("--nome", prompt=True, help="Nome do usuario.")
@click.option("--email", prompt=True, help="Email institucional do usuario.")
@click.option(
    "--perfil",
    prompt=True,
    type=click.Choice([perfil.value for perfil in PerfilUsuario], case_sensitive=False),
    help="Perfil persistido do usuario.",
)
@click.option(
    "--senha",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Senha inicial do usuario.",
)
def criar_usuario(nome: str, email: str, perfil: str, senha: str) -> None:
    """Cria um usuario persistido para acesso autenticado ao VITTAL."""
    usuario_service = UsuarioService()

    try:
        usuario = usuario_service.cadastrar_usuario(
            {
                "nome": nome,
                "email": email,
                "senha": senha,
                "perfil": perfil,
            }
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Usuario criado com sucesso: {usuario.email} ({usuario.perfil.value})")


@auth_cli.command("criar-coordenador-inicial")
def criar_coordenador_inicial() -> None:
    """Cria o primeiro coordenador de desenvolvimento de forma idempotente."""
    usuario_repository = UsuarioRepository()
    existente = usuario_repository.buscar_por_email(COORDENADOR_INICIAL_EMAIL)

    if existente is not None:
        if existente.perfil != PerfilUsuario.COORDENADOR:
            raise click.ClickException("Email inicial ja existe com perfil diferente de COORDENADOR.")

        click.echo(f"Coordenador inicial ja existe: {existente.email}")
        return

    usuario = UsuarioService(
        usuario_repository=usuario_repository,
        auth_service=AuthService(usuario_repository),
    ).cadastrar_usuario(
        {
            "nome": COORDENADOR_INICIAL_NOME,
            "email": COORDENADOR_INICIAL_EMAIL,
            "senha": COORDENADOR_INICIAL_SENHA,
            "perfil": PerfilUsuario.COORDENADOR,
        }
    )
    click.echo(f"Coordenador inicial criado: {usuario.email}")
