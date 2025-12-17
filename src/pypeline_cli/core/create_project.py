from .managers.project_context import ProjectContext
from .managers.toml_manager import TOMLManager


def create_project(ctx: ProjectContext, name: str):
    toml_manager = TOMLManager(ctx=ctx, name=name)

    print(type(toml_manager))
