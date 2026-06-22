import click
from flask.cli import AppGroup

from app.services.problem_type_service import ProblemTypeService

problem_types_cli = AppGroup("problem-types")


@problem_types_cli.command("seed")
def seed_problem_types() -> None:
    """Create the starter maintenance taxonomy without duplicating existing codes."""
    result = ProblemTypeService().seed_initial_problem_types()
    click.echo(
        "Problem type seed finished: "
        f"{result['created']} created, {result['skipped']} skipped."
    )
