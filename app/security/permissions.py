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


def pode_gerenciar_usuarios(usuario) -> bool:
    """Centraliza o acesso administrativo ao bloco de usuarios."""
    return pode_criar_usuarios(usuario)


def pode_visualizar_dashboard(usuario) -> bool:
    """Valida acesso ao dashboard conforme perfil e permissao persistida."""
    if not usuario or not usuario.is_authenticated or not usuario.ativo:
        return False

    if usuario.perfil == PerfilUsuario.COORDENADOR:
        return True

    return bool(getattr(usuario, "pode_visualizar_dashboard", False))


def can_view_laboratories(usuario) -> bool:
    """Any active authenticated user can access the internal laboratory view."""
    return bool(usuario and usuario.is_authenticated and usuario.ativo)


def can_manage_laboratories(usuario) -> bool:
    """Technicians and coordinators can manage institutional laboratories."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def can_view_workstations(usuario) -> bool:
    """Any active authenticated user can access internal workstation views."""
    return bool(usuario and usuario.is_authenticated and usuario.ativo)


def can_manage_workstations(usuario) -> bool:
    """Technicians and coordinators can manage workstation positions."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def can_view_computer_cases(usuario) -> bool:
    """Technicians and coordinators can inspect the technical inventory."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def can_manage_computer_cases(usuario) -> bool:
    """Only technicians can register or update computer case inventory data."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO)


def can_view_monitors(usuario) -> bool:
    """Technicians and coordinators can inspect monitor inventory."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def can_manage_monitors(usuario) -> bool:
    """Only technicians can register or update monitor inventory data."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO)


def can_view_asset_allocations(usuario) -> bool:
    """Technicians and coordinators can inspect workstation asset bindings."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def can_manage_asset_allocations(usuario) -> bool:
    """Only technicians can bind or unbind assets from workstations."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO)


def can_view_problem_types(usuario) -> bool:
    """Technicians and coordinators maintain the internal maintenance taxonomy."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def can_manage_problem_types(usuario) -> bool:
    """Problem type maintenance is restricted to technical and coordination roles."""
    return usuario_tem_perfil(usuario, PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)


def perfis_criaveis_por(usuario) -> tuple[PerfilUsuario, ...]:
    if not pode_criar_usuarios(usuario):
        return ()

    return PERFIS_CRIAVEIS_POR_COORDENADOR


def garantir_pode_criar_usuario(usuario, perfil: PerfilUsuario) -> None:
    if not pode_criar_usuarios(usuario):
        raise PermissionError("Usuario autenticado nao pode criar usuarios.")

    if perfil not in PERFIS_CRIAVEIS_POR_COORDENADOR:
        raise PermissionError("Perfil nao permitido para criacao de usuario.")
