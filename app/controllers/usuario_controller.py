from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.security.decorators import permissao_requerida
from app.security.permissions import pode_criar_usuarios, pode_gerenciar_usuarios
from app.services.usuario_service import UsuarioService

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.get("")
@permissao_requerida(pode_gerenciar_usuarios)
def listar_usuarios():
    """Lista usuarios persistidos para administracao pelo coordenador."""
    usuario_service = UsuarioService()
    return render_template(
        "usuarios/lista.html",
        usuarios=usuario_service.listar_usuarios(),
    )


@usuarios_bp.get("/novo")
@permissao_requerida(pode_criar_usuarios)
def novo_usuario():
    """Exibe formulario de criacao de usuario restrito a coordenadores."""
    usuario_service = UsuarioService()
    return render_template(
        "usuarios/novo.html",
        perfis=usuario_service.perfis_criaveis_por(current_user),
    )


@usuarios_bp.post("/novo")
@permissao_requerida(pode_criar_usuarios)
def criar_usuario():
    """Cria usuario persistido a partir da acao de um coordenador autenticado."""
    usuario_service = UsuarioService()
    try:
        usuario = usuario_service.cadastrar_usuario(
            dados=request.form,
            ator=current_user,
        )
    except (PermissionError, ValueError) as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "usuarios/novo.html",
                perfis=usuario_service.perfis_criaveis_por(current_user),
            ),
            400,
        )

    flash(f"Usuario criado com sucesso: {usuario.email}", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


@usuarios_bp.get("/<int:usuario_id>/editar")
@permissao_requerida(pode_gerenciar_usuarios)
def editar_usuario(usuario_id: int):
    """Exibe os dados administrativos editaveis de um usuario."""
    usuario_service = UsuarioService()
    usuario = _buscar_usuario_ou_404(usuario_service, usuario_id)
    return render_template(
        "usuarios/editar.html",
        usuario=usuario,
        perfis=usuario_service.perfis_criaveis_por(current_user),
    )


@usuarios_bp.post("/<int:usuario_id>/editar")
@permissao_requerida(pode_gerenciar_usuarios)
def atualizar_usuario(usuario_id: int):
    """Atualiza nome e email mantendo senha e historico de autenticacao."""
    usuario_service = UsuarioService()
    usuario = _buscar_usuario_ou_404(usuario_service, usuario_id)
    try:
        usuario_service.atualizar_usuario(usuario, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "usuarios/editar.html",
                usuario=usuario,
                perfis=usuario_service.perfis_criaveis_por(current_user),
            ),
            400,
        )

    flash("Usuario atualizado com sucesso.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


@usuarios_bp.post("/<int:usuario_id>/perfil")
@permissao_requerida(pode_gerenciar_usuarios)
def alterar_perfil(usuario_id: int):
    """Altera o perfil persistido do usuario conforme perfis permitidos."""
    usuario_service = UsuarioService()
    usuario = _buscar_usuario_ou_404(usuario_service, usuario_id)
    try:
        usuario_service.alterar_perfil(usuario, request.form.get("perfil", ""))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("usuarios.editar_usuario", usuario_id=usuario.id))

    flash("Perfil atualizado com sucesso.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


@usuarios_bp.post("/<int:usuario_id>/status")
@permissao_requerida(pode_gerenciar_usuarios)
def alterar_status_usuario(usuario_id: int):
    """Ativa ou desativa usuario persistido sem remover seu historico."""
    usuario_service = UsuarioService()
    usuario = _buscar_usuario_ou_404(usuario_service, usuario_id)
    usuario_service.alterar_status_usuario(usuario, request.form.get("ativo") == "true")
    flash("Status do usuario atualizado com sucesso.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


@usuarios_bp.post("/<int:usuario_id>/dashboard")
@permissao_requerida(pode_gerenciar_usuarios)
def definir_permissao_dashboard(usuario_id: int):
    """Define permissao persistida para acesso ao dashboard de validacao."""
    usuario_service = UsuarioService()
    usuario = _buscar_usuario_ou_404(usuario_service, usuario_id)
    usuario_service.definir_permissao_dashboard(
        usuario,
        request.form.get("pode_visualizar_dashboard") == "true",
    )
    flash("Permissao de dashboard atualizada com sucesso.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))


def _buscar_usuario_ou_404(usuario_service: UsuarioService, usuario_id: int):
    try:
        return usuario_service.buscar_usuario(usuario_id)
    except LookupError:
        abort(404)
