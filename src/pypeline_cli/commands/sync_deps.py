import click

from pathlib import Path

from ..core.managers.project_context import ProjectContext
from ..core.managers.dependencies_manager import DependenciesManager
from ..core.managers.toml_manager import TOMLManager


@click.command
def sync_deps():
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)

    dependencies_manager = DependenciesManager(ctx=ctx)

    toml_manager = TOMLManager(ctx=ctx)

    # Read dependencies file
    dependencies = dependencies_manager.read_user_dependencies()

    # Write changes to toml
    toml_manager.update_dependencies(
        key="project.dependencies", updated_data=dependencies
    )

    click.echo(dependencies)
