from pathlib import Path

from .managers.project_context import ProjectContext
from .managers.toml_manager import TOMLManager
from .managers.dependencies_manager import DependenciesManager
from .managers.license_manager import LicenseManager
from .managers.scaffolding_manager import ScaffoldingManager
from ..config import INIT_SCAFFOLD_FILES


def create_project(
    ctx: ProjectContext,
    name: str,
    author_name: str,
    author_email: str,
    description: str,
    license: str,
    company_name: str,
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

    # Create license
    license_manager = LicenseManager(ctx=ctx)
    license_manager.create(
        name=name,
        author_name=author_name,
        author_email=author_email,
        description=description,
        license=license,
        company_name=company_name,
    )

    # Create initializer scaffolds
    scaffolding_manager = ScaffoldingManager(ctx=ctx)
    scaffolding_manager.create_folder_scaffolding(
        [
            ctx.pipelines_folder_path,
            ctx.schemas_folder_path,
            ctx.integration_tests_folder_path,
            ctx.project_utils_folder_path,
        ]
    )

    scaffolding_manager.create_files_from_templates(scaffold_files=INIT_SCAFFOLD_FILES)
