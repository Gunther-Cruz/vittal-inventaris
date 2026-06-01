from flask import Blueprint, render_template

from app.security.decorators import permissao_requerida
from app.security.permissions import pode_visualizar_dashboard

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("")
@permissao_requerida(pode_visualizar_dashboard)
def index():
    """Tela temporaria para validar permissao antes dos dashboards reais."""
    return render_template("dashboard/index.html")
