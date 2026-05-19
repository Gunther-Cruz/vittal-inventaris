from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.domain.enums import PerfilUsuario
from app.security.decorators import perfis_requeridos
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.perfil"))

    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for("auth.perfil"))

    email = request.form.get("email", "")
    senha = request.form.get("senha", "")
    usuario = AuthService().autenticar(email, senha)

    if usuario is None:
        flash("Email ou senha invalidos.", "error")
        return render_template("auth/login.html"), 401

    login_user(usuario)

    next_url = request.args.get("next")
    if next_url and _is_safe_next(next_url):
        return redirect(next_url)

    return redirect(url_for("auth.perfil"))


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessao encerrada com sucesso.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.get("/perfil")
@login_required
def perfil():
    return render_template("auth/perfil.html")


@auth_bp.get("/area-tecnica")
@perfis_requeridos(PerfilUsuario.TECNICO, PerfilUsuario.COORDENADOR)
def area_tecnica():
    return render_template("auth/area_tecnica.html")


def _is_safe_next(next_url: str) -> bool:
    target = urlsplit(next_url)
    return next_url.startswith("/") and target.scheme == "" and target.netloc == ""
