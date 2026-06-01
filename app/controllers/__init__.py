from flask import Flask

from app.controllers.auth_controller import auth_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.health_controller import health_bp
from app.controllers.usuario_controller import usuarios_bp


def register_controllers(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(usuarios_bp)
