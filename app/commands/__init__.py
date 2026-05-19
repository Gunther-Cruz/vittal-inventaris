from flask import Flask

from app.commands.auth_commands import auth_cli


def register_commands(app: Flask) -> None:
    app.cli.add_command(auth_cli)
