from flask import Flask

from app.controllers.auth_controller import auth_bp
from app.controllers.computer_case_controller import computer_cases_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.health_controller import health_bp
from app.controllers.laboratory_controller import laboratories_bp
from app.controllers.monitor_controller import monitors_bp
from app.controllers.public_controller import public_bp
from app.controllers.usuario_controller import usuarios_bp
from app.controllers.workstation_controller import workstations_bp


def register_controllers(app: Flask) -> None:
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(computer_cases_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(laboratories_bp)
    app.register_blueprint(monitors_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(workstations_bp)
