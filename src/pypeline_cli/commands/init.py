import click

from ..utils.resolve_path import resolve_path
from ..core.create_project import create_project
from ..utils.valdators import validate_params
from ..core.managers.project_context import ProjectContext
from ..config import ALLOWED_LICENSE


@click.command()
@click.option(
    "--destination",
    prompt="Please enter the destination path of new etl package root",
    help="Destination path of new etl package root.",
)
@click.option(
    "--name", prompt="Please enter the name of the project", help="Name of the project."
)
@click.option(
    "--author-name", prompt="Please enter your name", help="Name of the author."
)
@click.option(
    "--author-email", prompt="Please enter your email", help="Email of the author."
)
@click.option(
    "--description",
    prompt="Please enter a description of this project",
    help="Description of the project.",
)
@click.option(
    "--license",
    type=click.Choice(ALLOWED_LICENSE, case_sensitive=False),
    prompt="Select license type",
    default="MIT",
    help="License type",
    show_choices=True,
)
def init(
    destination: str,
    name: str,
    author_name: str,
    author_email: str,
    description: str,
    license: str,
):
    """Create new ETL pipeline architecture"""

    # Validate all parameters at once
    validate_params(name=name, author_email=author_email, license=license)

    path = resolve_path(destination=destination, action="creating project", name=name)

    click.echo(f"Creating the {name} project at {path}")

    ctx = ProjectContext(path, init=True)

    if path:
        create_project(
            ctx=ctx,
            name=name,
            author_name=author_name,
            author_email=author_email,
            description=description,
            license=license,
            path=path,
        )
