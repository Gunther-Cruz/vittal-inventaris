from flask import Flask

from app.config import get_config
from app.controllers import register_controllers
from app.commands import register_commands
from app.extensions import csrf, db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    from app.domain import models  # noqa: F401

    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faca login para acessar esta area."
    login_manager.login_message_category = "warning"

    register_controllers(app)
    register_commands(app)

    return app


@login_manager.user_loader
def load_user(user_id: str):
    from app.repositories.usuario_repository import UsuarioRepository

    if not user_id.isdigit():
        return None

    usuario = UsuarioRepository().buscar_por_id(int(user_id))
    if usuario is None or not usuario.ativo:
        return None

    return usuario
