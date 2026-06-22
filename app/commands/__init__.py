from flask import Flask

from app.commands.auth_commands import auth_cli
from app.commands.problem_type_commands import problem_types_cli


def register_commands(app: Flask) -> None:
    app.cli.add_command(auth_cli)
    app.cli.add_command(problem_types_cli)
