from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import abort
from flask_login import current_user, login_required

from app.domain.enums import PerfilUsuario
from app.security.permissions import usuario_tem_perfil


def perfis_requeridos(*perfis: PerfilUsuario):
    """Protege rotas por perfil usando a politica central de permissoes."""
    def decorator(view_func: Callable[..., Any]):
        @wraps(view_func)
        @login_required
        def wrapper(*args: Any, **kwargs: Any):
            if not usuario_tem_perfil(current_user, *perfis):
                abort(403)

            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def permissao_requerida(verificador: Callable[[Any], bool]):
    """Protege rotas por uma regra de permissao nomeada."""
    def decorator(view_func: Callable[..., Any]):
        @wraps(view_func)
        @login_required
        def wrapper(*args: Any, **kwargs: Any):
            if not verificador(current_user):
                abort(403)

            return view_func(*args, **kwargs)

        return wrapper

    return decorator
