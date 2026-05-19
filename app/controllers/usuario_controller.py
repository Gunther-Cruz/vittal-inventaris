from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.security.decorators import permissao_requerida
from app.security.permissions import pode_criar_usuarios
from app.services.auth_service import AuthService

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.get("/novo")
@permissao_requerida(pode_criar_usuarios)
def novo_usuario():
    """Exibe formulario de criacao de usuario restrito a coordenadores."""
    auth_service = AuthService()
    return render_template(
        "usuarios/novo.html",
        perfis=auth_service.perfis_criaveis_por(current_user),
    )


@usuarios_bp.post("/novo")
@permissao_requerida(pode_criar_usuarios)
def criar_usuario():
    """Cria usuario persistido a partir da acao de um coordenador autenticado."""
    auth_service = AuthService()
    try:
        usuario = auth_service.criar_usuario_por_coordenador(
            coordenador=current_user,
            nome=request.form.get("nome", ""),
            email=request.form.get("email", ""),
            senha=request.form.get("senha", ""),
            perfil=request.form.get("perfil", ""),
        )
    except (PermissionError, ValueError) as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "usuarios/novo.html",
                perfis=auth_service.perfis_criaveis_por(current_user),
            ),
            400,
        )

    flash(f"Usuario criado com sucesso: {usuario.email}", "success")
    return redirect(url_for("auth.perfil"))
