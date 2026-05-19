from app.domain.enums import PerfilUsuario

PERFIS_CRIAVEIS_POR_COORDENADOR = (
    PerfilUsuario.PROFESSOR,
    PerfilUsuario.TECNICO,
    PerfilUsuario.COORDENADOR,
)


def usuario_tem_perfil(usuario, *perfis: PerfilUsuario) -> bool:
    """Verifica perfis sem espalhar comparacoes diretas pelas rotas."""
    return bool(usuario and usuario.is_authenticated and usuario.perfil in perfis)


def pode_criar_usuarios(usuario) -> bool:
    """Somente coordenadores podem criar usuarios persistidos no VITTAL."""
    return usuario_tem_perfil(usuario, PerfilUsuario.COORDENADOR)


def perfis_criaveis_por(usuario) -> tuple[PerfilUsuario, ...]:
    if not pode_criar_usuarios(usuario):
        return ()

    return PERFIS_CRIAVEIS_POR_COORDENADOR


def garantir_pode_criar_usuario(usuario, perfil: PerfilUsuario) -> None:
    if not pode_criar_usuarios(usuario):
        raise PermissionError("Usuario autenticado nao pode criar usuarios.")

    if perfil not in PERFIS_CRIAVEIS_POR_COORDENADOR:
        raise PermissionError("Perfil nao permitido para criacao de usuario.")
