import click

from ..utils.resolve_path import resolve_path
from ..core.create_project import create_project
from ..utils.valdators import validate_project_name
from ..core.managers.project_context import ProjectContext


@click.command()
@click.option(
    "--destination",
    prompt="Please enter the destination path of new etl package root.",
    help="Destination path of new etl package root.",
)
@click.option("--name", help="Name of the project.")
def init(destination: str, name: str):
    """Create new ETL pipeline architecture"""

    is_valid, error_message = validate_project_name(name)
    if not is_valid:
        raise click.BadParameter(error_message, param_hint="'--name'")

    path = resolve_path(destination=destination, action="creating project", name=name)

    click.echo(f"Creating the {name} project at {path}")

    ctx = ProjectContext(path, init=True)

    if path:
        create_project(ctx=ctx, name=name)
