# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pypeline-cli is a CLI tool that scaffolds data pipeline projects with opinionated templates and dependency management. It generates complete project structures with Snowflake-focused utilities, manages dependencies via a user-friendly Python file, and handles git initialization.

## Development Commands

### Setup for Development
```bash
# Install in editable mode globally
pip install -e .

# The pypeline command will now reflect local code changes immediately
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_basic.py

# Run tests without coverage
pytest --no-cov
```

### Code Quality
```bash
# Format and lint code
ruff format .
ruff check .

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Building and Distribution
```bash
# Build distribution packages
python -m build

# Check distribution
twine check dist/*

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Architecture

### Manager Pattern
The codebase uses a manager pattern where specialized managers handle different aspects of project creation:

- **ProjectContext** (`core/managers/project_context.py`): Discovers project root by walking up the directory tree looking for `pyproject.toml` with `[tool.pypeline]` marker. Provides all path properties as dynamic computed attributes (e.g., `ctx.project_root`, `ctx.toml_path`, `ctx.dependencies_path`).

- **TOMLManager** (`core/managers/toml_manager.py`): Handles `pyproject.toml` read/write operations. Uses `tomllib` (Python 3.11+) or `tomli` (Python 3.10) for reading, `tomli_w` for writing. The `update_dependencies()` method parses existing deps, merges new ones by package name, and writes back.

- **DependenciesManager** (`core/managers/dependencies_manager.py`): Reads `DEFAULT_DEPENDENCIES` from user's `dependencies.py` file and manages the template file creation.

- **LicenseManager** (`core/managers/license_manager.py`): Creates LICENSE files from templates in `templates/licenses/`, performing variable substitution for author name, year, etc.

- **ScaffoldingManager** (`core/managers/scaffolding_manager.py`): Creates folder structure and copies template files to destination paths using the `ScaffoldFile` dataclass configuration.

- **GitManager** (`core/managers/git_manager.py`): Initializes git repos and creates initial commits with proper line ending configuration.

### Core Flow

The `init` command flow:
1. Creates ProjectContext with `init=True` (uses provided path, doesn't search for existing project)
2. Creates project directory and initializes git
3. Creates `.gitattributes` for consistent line endings
4. TOMLManager creates `pyproject.toml` with hatch-vcs configuration
5. DependenciesManager creates `dependencies.py` from template
6. LicenseManager creates LICENSE file
7. ScaffoldingManager creates folder structure (src, tests, pipelines, schemas, utils)
8. ScaffoldingManager copies all template files from `config.INIT_SCAFFOLD_FILES`

The `sync-deps` command flow:
1. ProjectContext searches up tree for pypeline project (looks for `[tool.pypeline]` in pyproject.toml)
2. DependenciesManager reads `DEFAULT_DEPENDENCIES` from user's `dependencies.py`
3. TOMLManager parses dependencies with `dependency_parser.py`, merges by package name, and writes to `pyproject.toml`

### Template System

Templates are stored in `src/pypeline_cli/templates/`:
- `init/` - Project scaffolding templates (databases.py, etl.py, tables.py, etc.)
- `licenses/` - 14 different license templates with variable substitution

The `config.py` file defines `INIT_SCAFFOLD_FILES` list that maps template files to ProjectContext properties for destination paths.

### Dependency Management Philosophy

pypeline projects use a two-file approach:
1. `dependencies.py` - User-editable Python list (`DEFAULT_DEPENDENCIES`)
2. `pyproject.toml` - Auto-generated via `pypeline sync-deps`

The `dependency_parser.py` utility handles parsing dependency strings with version specifiers (>=, ==, ~=, etc.) into `Dependency` namedtuples for manipulation.

## Python Version Compatibility

**Critical**: This codebase must support Python 3.10+ because:
- Generated projects target Snowflake compatibility (requires 3.10+)
- The CLI itself declares `requires-python = ">=3.10"`

**Compatibility pattern for tomllib**:
```python
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
```

This pattern is used in `toml_manager.py` and `project_context.py` because `tomllib` is stdlib in 3.11+ but requires the `tomli` backport for 3.10.

## Project Structure

```
pypeline-cli/
├── src/pypeline_cli/
│   ├── main.py              # Click group, registers commands
│   ├── config.py            # Constants, paths, scaffold configuration
│   ├── commands/            # Click command definitions
│   │   ├── init.py          # pypeline init
│   │   ├── sync_deps.py     # pypeline sync-deps
│   │   └── install.py       # pypeline install
│   ├── core/
│   │   ├── create_project.py     # Orchestrates project creation
│   │   └── managers/             # Manager classes for different concerns
│   ├── templates/
│   │   ├── init/                 # Template files for generated projects
│   │   └── licenses/             # License templates
│   └── utils/
│       ├── dependency_parser.py  # Parse dependency strings
│       └── valdators.py          # Input validation
└── tests/                        # Test files
```

## Key Conventions

- **Path handling**: Use `pathlib.Path` throughout, never string concatenation
- **Click output**: Use `click.echo()` for all user-facing messages, not `print()`
- **Template naming**: Templates end with `.template` extension
- **Manager initialization**: All managers receive `ProjectContext` instance
- **Version management**: Projects use hatch-vcs for git tag-based versioning
