from pathlib import Path
import tomllib


class ProjectContext:
    """Discovers and provides project paths dynamically."""

    def __init__(self, start_dir: Path, init: bool = False):
        if not init:
            self.project_root = self._find_project_root(start_dir)

        else:
            self.project_root = start_dir

    def _find_project_root(self, start_path: Path) -> Path:
        """Walk up directory tree to find pypeline's pyproject.toml"""
        current = start_path
        while current != current.parent:
            toml_path = current / "pyproject.toml"
            if toml_path.exists() and self._is_pypeline_project(toml_path):
                return current
            current = current.parent
        raise RuntimeError(
            "Not in a pypeline project (no pyproject.toml with [tool.pypeline] found)"
        )

    def _is_pypeline_project(self, toml_path: Path) -> bool:
        """Check if pyproject.toml is a pypeline-managed project"""
        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
            return "tool" in data and "pypeline" in data.get("tool", {})
        except Exception:
            # If we can't read/parse the toml, it's not a pypeline project
            return False

    @property
    def toml_path(self) -> Path:
        return self.project_root / "pyproject.toml"

    @property
    def platform(self) -> str:
        """
        Get platform from pyproject.toml.

        Returns:
            Platform string ("snowflake" or "databricks")

        Raises:
            ValueError: If platform not set in pyproject.toml
            FileNotFoundError: If pyproject.toml doesn't exist
        """
        if not self.toml_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {self.toml_path}")

        try:
            with open(self.toml_path, "rb") as f:
                data = tomllib.load(f)

            platform = data.get("tool", {}).get("pypeline", {}).get("platform")

            if platform is None:
                raise ValueError(
                    f"Platform not set in {self.toml_path}. "
                    "Add 'platform = \"snowflake\"' or 'platform = \"databricks\"' "
                    "to [tool.pypeline] section."
                )

            return platform
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Failed to parse {self.toml_path}: {e}")

    @property
    def import_folder(self) -> Path:
        return self.project_root / self.project_root.name

    @property
    def dependencies_path(self) -> Path:
        return self.project_root / "dependencies.py"

    @property
    def dependencies_template(self) -> Path:
        """Get platform-specific dependencies template path."""
        from ...config import get_platform_dependencies_template

        return get_platform_dependencies_template(self.platform)

    @property
    def licenses_path(self) -> Path:
        return self.project_root / "LICENSE"

    @property
    def pipelines_folder_path(self) -> Path:
        return self.import_folder / "pipelines"

    @property
    def schemas_folder_path(self) -> Path:
        return self.import_folder / "schemas"

    @property
    def integration_tests_folder_path(self) -> Path:
        return self.project_root / "tests"

    @property
    def project_utils_folder_path(self) -> Path:
        return self.import_folder / "utils"

    @property
    def databases_file(self) -> Path:
        return self.project_utils_folder_path / "databases.py"

    @property
    def date_parser_file(self) -> Path:
        return self.project_utils_folder_path / "date_parser.py"

    @property
    def decorators_file(self) -> Path:
        return self.project_utils_folder_path / "decorators.py"

    @property
    def etl_file(self) -> Path:
        return self.project_utils_folder_path / "etl.py"

    @property
    def logger_file(self) -> Path:
        return self.project_utils_folder_path / "logger.py"

    @property
    def platform_utils_file(self) -> Path:
        """Get platform-specific utils file path (snowflake_utils.py or databricks_utils.py)."""
        return self.project_utils_folder_path / f"{self.platform}_utils.py"

    @property
    def basic_test_file(self) -> Path:
        return self.integration_tests_folder_path / "basic_test.py"

    @property
    def gitignore_file(self) -> Path:
        return self.project_root / ".gitignore"

    @property
    def init_readme_file(self) -> Path:
        return self.project_root / "README.md"

    @property
    def _init_file(self) -> Path:
        return self.import_folder / "__init__.py"

    @property
    def table_cache_file(self) -> Path:
        return self.project_utils_folder_path / "table_cache.py"

    @property
    def types_file(self) -> Path:
        return self.project_utils_folder_path / "types.py"

    @property
    def credentials_file(self) -> Path:
        return self.project_root / "credentials.py"

    @property
    def credentials_example_file(self) -> Path:
        return self.project_root / "credentials.py.example"