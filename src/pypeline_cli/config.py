from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import tomllib


class Platform(str, Enum):
    """Supported platforms for pypeline projects."""
    SNOWFLAKE = "snowflake"
    DATABRICKS = "databricks"


def get_platform_from_toml(toml_path: Path | None = None) -> str | None:
    """
    Read platform from pyproject.toml [tool.pypeline] section.

    Args:
        toml_path: Path to pyproject.toml file. If None, searches for it in current directory.

    Returns:
        Platform string ("snowflake" or "databricks") or None if not found.

    Raises:
        FileNotFoundError: If toml_path provided but doesn't exist
    """
    if toml_path is None:
        toml_path = Path.cwd() / "pyproject.toml"

    if not toml_path.exists():
        if toml_path == Path.cwd() / "pyproject.toml":
            return None  # Not found in current directory
        raise FileNotFoundError(f"pyproject.toml not found at {toml_path}")

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)

        platform = data.get("tool", {}).get("pypeline", {}).get("platform")
        return platform
    except Exception:
        return None


# Template path constants
PATH_TO_TEMPLATES = Path(__file__).parent / "templates"
PATH_TO_SHARED_INIT = PATH_TO_TEMPLATES / "shared" / "init"
PATH_TO_LICENSES = PATH_TO_TEMPLATES / "licenses"


def get_platform_init_path(platform: str) -> Path:
    """
    Get platform-specific init templates path.

    Args:
        platform: Platform name ("snowflake" or "databricks")

    Returns:
        Path to platform's init templates directory

    Example:
        >>> get_platform_init_path("snowflake")
        Path(".../templates/snowflake/init")
    """
    return PATH_TO_TEMPLATES / platform / "init"


def get_platform_pipelines_path(platform: str) -> Path:
    """
    Get platform-specific pipeline templates path.

    Args:
        platform: Platform name ("snowflake" or "databricks")

    Returns:
        Path to platform's pipeline templates directory

    Example:
        >>> get_platform_pipelines_path("databricks")
        Path(".../templates/databricks/pipelines")
    """
    return PATH_TO_TEMPLATES / platform / "pipelines"


def get_platform_processors_path(platform: str) -> Path:
    """
    Get platform-specific processor templates path.

    Args:
        platform: Platform name ("snowflake" or "databricks")

    Returns:
        Path to platform's processor templates directory

    Example:
        >>> get_platform_processors_path("snowflake")
        Path(".../templates/snowflake/processors")
    """
    return PATH_TO_TEMPLATES / platform / "processors"


def get_platform_dependencies_template(platform: str) -> Path:
    """
    Get platform-specific dependencies.py template path.

    Args:
        platform: Platform name ("snowflake" or "databricks")

    Returns:
        Path to platform's dependencies.py.template file

    Example:
        >>> get_platform_dependencies_template("snowflake")
        Path(".../templates/snowflake/init/dependencies.py.template")
    """
    return get_platform_init_path(platform) / "dependencies.py.template"


LICENSES = {
    "MIT": PATH_TO_LICENSES / "mit.txt",
    "Apache-2.0": PATH_TO_LICENSES / "apache_license_2_0.txt",
    "GPL-3.0": PATH_TO_LICENSES / "gnu_general_public_license_v3_0.txt",
    "GPL-2.0": PATH_TO_LICENSES / "gnu_general_public_license_v2_0.txt",
    "LGPL-2.1": PATH_TO_LICENSES / "gnu_lesser_general_public_license_v2_1.txt",
    "BSD-2-Clause": PATH_TO_LICENSES / "bsd_2_clause_license.txt",
    "BSD-3-Clause": PATH_TO_LICENSES / "bsd_3_clause_license.txt",
    "BSL-1.0": PATH_TO_LICENSES / "boost_software_license_1_0.txt",
    "CC0-1.0": PATH_TO_LICENSES / "creative_commons_zero_v1_0_universal.txt",
    "EPL-2.0": PATH_TO_LICENSES / "eclipse_public_license_2_0.txt",
    "AGPL-3.0": PATH_TO_LICENSES / "gnu_affero_general_public_license_v3_0.txt",
    "MPL-2.0": PATH_TO_LICENSES / "mozilla_public_license_2_0.txt",
    "Unlicense": PATH_TO_LICENSES / "the_unlicense.txt",
    "Proprietary": PATH_TO_LICENSES / "proprietary.txt",
}


@dataclass
class ScaffoldFile:
    """Configuration for a single scaffold file."""

    template_name: Path
    destination_property: str


# Shared scaffold files (platform-agnostic)
SHARED_SCAFFOLD_FILES = [
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "databases.py.template",
        destination_property="databases_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "date_parser.py.template",
        destination_property="date_parser_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "logger.py.template",
        destination_property="logger_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "types.py.template",
        destination_property="types_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "basic_test.py.template",
        destination_property="basic_test_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / ".gitignore.template",
        destination_property="gitignore_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "README.md.template",
        destination_property="init_readme_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_SHARED_INIT / "_init.py.template",
        destination_property="_init_file",
    ),
]


def get_platform_scaffold_files(platform: str) -> list[ScaffoldFile]:
    """
    Get combined shared and platform-specific scaffold files.

    Args:
        platform: Platform name ("snowflake" or "databricks")

    Returns:
        List of ScaffoldFile objects for project initialization,
        combining shared files with platform-specific files.

    Raises:
        ValueError: If platform is not supported

    Example:
        >>> files = get_platform_scaffold_files("snowflake")
        >>> len(files)  # 8 shared + 5 snowflake-specific
        13
    """
    if platform not in [Platform.SNOWFLAKE.value, Platform.DATABRICKS.value]:
        raise ValueError(
            f"Unsupported platform: {platform}. "
            f"Must be '{Platform.SNOWFLAKE.value}' or '{Platform.DATABRICKS.value}'"
        )

    platform_init_path = get_platform_init_path(platform)

    # Platform-specific files (same structure for both Snowflake and Databricks)
    platform_files = [
        ScaffoldFile(
            template_name=platform_init_path / "etl.py.template",
            destination_property="etl_file",
        ),
        ScaffoldFile(
            template_name=platform_init_path / "decorators.py.template",
            destination_property="decorators_file",
        ),
        ScaffoldFile(
            template_name=platform_init_path / "table_cache.py.template",
            destination_property="table_cache_file",
        ),
        ScaffoldFile(
            template_name=platform_init_path / "credentials.py.example.template",
            destination_property="credentials_example_file",
        ),
    ]

    # Platform-specific utils file (snowflake_utils.py or databricks_utils.py)
    platform_utils_file = ScaffoldFile(
        template_name=platform_init_path / f"{platform}_utils.py.template",
        destination_property="platform_utils_file",
    )
    platform_files.append(platform_utils_file)

    # Combine shared and platform-specific files
    return SHARED_SCAFFOLD_FILES + platform_files


# DEPRECATED: Use get_platform_scaffold_files() instead
# Kept for backwards compatibility - defaults to Snowflake platform
INIT_SCAFFOLD_FILES = get_platform_scaffold_files(Platform.SNOWFLAKE.value)
