from pathlib import Path
import tomli


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
                data = tomli.load(f)
            return "tool" in data and "pypeline" in data.get("tool", {})
        except Exception:
            # If we can't read/parse the toml, it's not a pypeline project
            return False

    @property
    def toml_path(self) -> Path:
        return self.project_root / "pyproject.toml"

    @property
    def src_path(self) -> Path:
        return self.project_root / "src"

    @property
    def tests_path(self) -> Path:
        return self.project_root / "tests"
