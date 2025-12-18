from pathlib import Path

from .managers.project_context import ProjectContext
from .managers.toml_manager import TOMLManager
from .managers.dependencies_manager import DependenciesManager


def create_project(
    ctx: ProjectContext,
    name: str,
    author_name: str,
    author_email: str,
    description: str,
    license: str,
    path: Path,
):
    # Create the project root
    Path.mkdir(path, parents=False, exist_ok=False)

    # Create TOML file
    toml_manager = TOMLManager(
        ctx=ctx,
    )

    toml_manager.create(
        name=name,
        author_name=author_name,
        author_email=author_email,
        description=description,
        license=license,
    )

    dependencies_manager = DependenciesManager(ctx=ctx)
    dependencies_manager.create()
