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

- **ProjectContext** (`core/managers/project_context.py`): Discovers project root by walking up the directory tree looking for `pyproject.toml` with `[tool.pypeline]` marker. Provides all path properties as dynamic computed attributes (e.g., `ctx.project_root`, `ctx.toml_path`, `ctx.dependencies_path`, `ctx.pipelines_folder_path`).

- **TOMLManager** (`core/managers/toml_manager.py`): Handles `pyproject.toml` read/write operations. Uses `tomllib` for reading, `tomli_w` for writing. The `update_dependencies()` method parses existing deps, merges new ones by package name, and writes back.

- **DependenciesManager** (`core/managers/dependencies_manager.py`): Reads `DEFAULT_DEPENDENCIES` from user's `dependencies.py` file and manages the template file creation.

- **LicenseManager** (`core/managers/license_manager.py`): Creates LICENSE files from templates in `templates/licenses/`, performing variable substitution for author name, year, etc. Uses `string.Template` for variable substitution.

- **ScaffoldingManager** (`core/managers/scaffolding_manager.py`): Creates folder structure and copies template files to destination paths using the `ScaffoldFile` dataclass configuration.

- **PipelineManager** (`core/managers/pipeline_manager.py`): Creates pipeline folder structures with runner, config, tests, and processors directories. Uses `string.Template` for variable substitution in templates. Automatically registers pipeline classes in the package's `__init__.py` for top-level imports.

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

The `create-pipeline` command flow:
1. Validates and normalizes pipeline name (accepts hyphens, converts to underscores)
2. Converts to PascalCase with "Pipeline" suffix (e.g., `beneficiary-claims` → `BeneficiaryClaimsPipeline`)
3. ProjectContext searches up tree for pypeline project (init=False mode)
4. Creates pipeline folder structure:
   - `pipelines/{name}/{name}_runner.py` - Main pipeline orchestrator
   - `pipelines/{name}/config.py` - Pipeline-specific configuration with TableConfig imports
   - `pipelines/{name}/README.md` - Pipeline documentation template
   - `pipelines/{name}/processors/` - Directory for processor classes
   - `pipelines/{name}/tests/` - Integration tests for the pipeline
5. PipelineManager registers pipeline class in package `__init__.py` for top-level imports
6. Updates `__all__` list in `__init__.py` for explicit exports

### Template System

Templates are stored in `src/pypeline_cli/templates/`:
- `init/` - Project scaffolding templates (databases.py, etl.py, tables.py, etc.)
- `licenses/` - 14 different license templates with variable substitution
- `pipelines/` - Pipeline templates with variable substitution:
  - `runner.py.template` - Pipeline orchestrator with run(), pipeline(), run_processors(), _write_to_snowflake()
  - `config.py.template` - Pipeline configuration with Database, Schema, TableConfig imports
  - `README.md.template` - Pipeline documentation structure
  - `processors_init.py.template` - Processors package marker
  - `tests_init.py.template` - Integration tests package marker

The `config.py` file defines `INIT_SCAFFOLD_FILES` list that maps template files to ProjectContext properties for destination paths.

**Template Variable Substitution**:
Pipeline templates use `string.Template` with variables:
- `$class_name` - PascalCase class name with "Pipeline" suffix (e.g., "BeneficiaryClaimsPipeline")
- `$pipeline_name` - Normalized name (e.g., "beneficiary_claims")
- `$project_name` - Project name from ProjectContext for import paths

### Dependency Management Philosophy

pypeline projects use a two-file approach:
1. `dependencies.py` - User-editable Python list (`DEFAULT_DEPENDENCIES`)
2. `pyproject.toml` - Auto-generated via `pypeline sync-deps`

The `dependency_parser.py` utility handles parsing dependency strings with version specifiers (>=, ==, ~=, etc.) into `Dependency` namedtuples for manipulation.

## Python Version Compatibility

**Critical**: This codebase requires Python 3.12-3.13 because:
- Generated projects target Snowflake compatibility (snowflake-snowpark-python supports up to Python 3.13)
- The CLI itself declares `requires-python = ">=3.12"`
- Generated projects declare `requires-python = ">=3.12,<3.14"`
- `tomllib` is part of stdlib in Python 3.11+, so no compatibility shim needed

**TOML handling**:
```python
import tomllib  # For reading TOML (stdlib in 3.11+)
import tomli_w  # For writing TOML (separate package)
```

This simplified approach is used in `toml_manager.py` and `project_context.py`.

## Project Structure

```
pypeline-cli/
├── src/pypeline_cli/
│   ├── main.py              # Click group, registers commands
│   ├── config.py            # Constants, paths, scaffold configuration
│   ├── commands/            # Click command definitions
│   │   ├── init.py          # pypeline init
│   │   ├── sync_deps.py     # pypeline sync-deps
│   │   ├── install.py       # pypeline install
│   │   └── create_pipeline.py   # pypeline create-pipeline
│   ├── core/
│   │   ├── create_project.py     # Orchestrates project creation
│   │   └── managers/             # Manager classes for different concerns
│   │       ├── project_context.py
│   │       ├── toml_manager.py
│   │       ├── dependencies_manager.py
│   │       ├── license_manager.py
│   │       ├── scaffolding_manager.py
│   │       ├── pipeline_manager.py   # NEW: Pipeline creation
│   │       └── git_manager.py
│   ├── templates/
│   │   ├── init/                 # Template files for generated projects
│   │   ├── licenses/             # License templates
│   │   └── pipelines/            # NEW: Pipeline templates
│   │       ├── runner.py.template
│   │       ├── config.py.template
│   │       ├── README.md.template
│   │       ├── processors_init.py.template
│   │       └── tests_init.py.template
│   └── utils/
│       ├── dependency_parser.py  # Parse dependency strings
│       ├── valdators.py          # Input validation
│       └── name_converter.py     # NEW: Name normalization/conversion
└── tests/                        # Test files
```

## Pipeline Architecture

### Generated Pipeline Structure

When `pypeline create-pipeline --name beneficiary-claims` is run, it creates:

```
pipelines/beneficiary_claims/
├── beneficiary_claims_runner.py    # Main orchestrator
├── config.py                        # Pipeline-specific config with TableConfig
├── README.md                        # Pipeline documentation
├── processors/                      # Processor classes go here
│   └── __init__.py
└── tests/                           # Integration tests
    └── __init__.py
```

### Pipeline Runner Pattern

The generated runner follows this architecture (from scratch.py):

```python
class BeneficiaryClaimsPipeline:
    def __init__(self):
        self.logger = Logger()
        self.etl = ETL()

    @time_function("BeneficiaryClaimsPipeline.run")
    def run(self, _write: bool = False):
        """Entry point with timing decorator"""
        self.pipeline(_write)

    def pipeline(self, _write: bool):
        """Orchestrates processors and conditional write"""
        df = self.run_processors()
        if _write:
            self._write_to_snowflake(df, ...)

    def run_processors(self) -> DataFrame:
        """Instantiates and runs processor classes"""
        # Processors import from ./processors/
        # Each processor handles its own extract in __init__ using TableConfig
        # Each processor has process() method for transformations

    def _write_to_snowflake(self, df, write_mode, table_path):
        """Uses df.write.mode().save_as_table()"""
```

### Processor Pattern (User-Created)

Processors (created by users, will have `create-processor` command later):
- Handle data extraction in `__init__` using TableConfig from `utils/tables.py`
- Implement `process()` method as orchestrator for transformations
- Use private methods for atomized transformation steps
- Return DataFrames

### Auto-Registration

Pipeline classes are automatically registered in the package's `__init__.py`:

```python
# Generated in src/{project_name}/__init__.py
from .pipelines.beneficiary_claims.beneficiary_claims_runner import BeneficiaryClaimsPipeline

__all__ = ["BeneficiaryClaimsPipeline"]
```

This allows users to import pipelines directly:
```python
from my_project import BeneficiaryClaimsPipeline, EnrollmentPipeline
```

### Naming Conventions

- **Input**: User provides name (e.g., `beneficiary-claims`, `enrollment`, `CLAIMS`)
- **Normalization**: Convert to lowercase with underscores (e.g., `beneficiary_claims`)
- **Folder/File**: Use normalized name (e.g., `pipelines/beneficiary_claims/beneficiary_claims_runner.py`)
- **Class Name**: PascalCase + "Pipeline" suffix (e.g., `BeneficiaryClaimsPipeline`)
- **Import**: Registered in `__init__.py` for top-level package import

Handled by `utils/name_converter.py`:
- `normalize_name()` - Strips whitespace, lowercases, converts hyphens to underscores
- `to_pascal_case()` - Converts normalized name to PascalCase
- Command adds "Pipeline" suffix to class name

## Key Conventions

- **Path handling**: Use `pathlib.Path` throughout, never string concatenation
- **Click output**: Use `click.echo()` for all user-facing messages, not `print()`
- **Template naming**: Templates end with `.template` extension
- **Manager initialization**: All managers receive `ProjectContext` instance
- **Version management**: Projects use hatch-vcs for git tag-based versioning
- **Pipeline naming**: Class names always have "Pipeline" suffix (e.g., `BeneficiaryClaimsPipeline`)
