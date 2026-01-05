# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pypeline-cli is a highly-opinionated, batteries-included lightweight framework for building Snowflake ETL pipelines with Snowpark. It scaffolds production-ready data pipeline projects with built-in session management, logging, table configuration, and a proven Extract-Transform-Load pattern. The framework generates complete project structures with Snowflake-focused utilities, manages dependencies via a user-friendly Python file, and provides runtime components (ETL singleton, Logger, decorators) that enforce best practices.

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

## Refactoring Progress

### Task 1.1: Create Template Directory Structure ✅

- Created new template directory structure: `templates/shared/`, `templates/snowflake/`, `templates/databricks/`
- Each platform directory contains: `init/`, `pipelines/`, `processors/` subdirectories (currently empty)
- Existing template directories (`init/`, `pipelines/`, `processors/`) remain in place for now
- No code changes, directory structure only
- All tests pass

### Task 1.2: Organize Shared and Snowflake Templates ✅

- Moved 8 shared templates to `templates/shared/init/`: databases.py, date_parser.py, logger.py, types.py, basic_test.py, .gitignore, README.md, _init.py
- Moved 5 Snowflake-specific templates to `templates/snowflake/init/`: etl.py, snowflake_utils.py, decorators.py, table_cache.py, credentials.py.example
- Moved dependencies.py.template to `templates/snowflake/init/` with BASE_DEPENDENCIES structure
- Moved 5 pipeline templates to `templates/snowflake/pipelines/`: runner.py, config.py, README.md, processors_init.py, tests_init.py
- Moved 2 processor templates to `templates/snowflake/processors/`: processor.py, test_processor.py
- Removed original files from `templates/init/`, `templates/pipelines/`, `templates/processors/` (directories remain empty for now)

### Task 1.3: Update config.py with Platform Support ✅

- Added `Platform` enum with SNOWFLAKE and DATABRICKS values
- Added `get_platform_from_toml()` helper function to read platform from pyproject.toml [tool.pypeline] section
- Updated template path constants to use shared/platform structure:
  - `PATH_TO_TEMPLATES` - Base path for all templates
  - `PATH_TO_SHARED_INIT` - Platform-agnostic templates
  - Removed obsolete `PATH_TO_INIT_TEMPLATES`
- Added platform path helper functions:
  - `get_platform_init_path()` - Returns platform's init templates directory
  - `get_platform_pipelines_path()` - Returns platform's pipelines templates directory
  - `get_platform_processors_path()` - Returns platform's processors templates directory
  - `get_platform_dependencies_template()` - Returns platform's dependencies.py.template file
- Created `SHARED_SCAFFOLD_FILES` list with 8 platform-agnostic template references
- Added `get_platform_scaffold_files()` function that returns combined shared + platform-specific files
- Maintained backwards compatibility: `INIT_SCAFFOLD_FILES` now defaults to Snowflake platform
- Removed `DEFAULT_DEPENDENCIES` constant (now platform-specific in templates)
- Updated `toml_manager.py` to initialize empty dependencies list (populated via sync-deps)
- All template files verified to exist at expected paths
- All tests pass

## Architecture

### Manager Pattern
The codebase uses a manager pattern where specialized managers handle different aspects of project creation:

- **ProjectContext** (`core/managers/project_context.py`): Discovers project root by walking up the directory tree looking for `pyproject.toml` with `[tool.pypeline]` marker. Provides all path properties as dynamic computed attributes (e.g., `ctx.project_root`, `ctx.import_folder`, `ctx.dependencies_path`, `ctx.pipelines_folder_path`).

- **TOMLManager** (`core/managers/toml_manager.py`): Handles `pyproject.toml` read/write operations. Uses `tomllib` for reading, `tomli_w` for writing. The `update_dependencies()` method parses existing deps, merges new ones by package name, and writes back. Creates pyproject.toml with empty dependencies list (populated via sync-deps).

- **DependenciesManager** (`core/managers/dependencies_manager.py`): Reads `DEFAULT_DEPENDENCIES` from user's `dependencies.py` file and manages the template file creation. Dependencies are now platform-specific, defined in each platform's dependencies.py.template file.

- **LicenseManager** (`core/managers/license_manager.py`): Creates LICENSE files from templates in `templates/licenses/`, performing variable substitution for author name, year, etc. Uses `string.Template` for variable substitution.

- **ScaffoldingManager** (`core/managers/scaffolding_manager.py`): Creates folder structure and copies template files to destination paths using the `ScaffoldFile` dataclass configuration. Automatically creates `__init__.py` files in Python package folders (pipelines/, utils/, schemas/) to ensure proper package structure.

- **PipelineManager** (`core/managers/pipeline_manager.py`): Creates pipeline folder structures with runner, config, tests, and processors directories. Uses `string.Template` for variable substitution in templates. Automatically creates `__init__.py` in each pipeline folder and registers pipeline classes in the package's `__init__.py` for top-level imports.

- **ProcessorManager** (`core/managers/processor_manager.py`): Creates processor classes within existing pipelines. Generates processor file with Extract/Transform pattern, test file with pytest fixtures, and auto-registers import in pipeline runner file. Uses `string.Template` for variable substitution.

- **GitManager** (`core/managers/git_manager.py`): Initializes git repos and creates initial commits with proper line ending configuration.

### Core Flow

The `init` command flow:
1. Creates ProjectContext with `init=True` (uses provided path, doesn't search for existing project)
2. Optionally creates project directory and initializes git (controlled by `--git/--no-git` flag, default: disabled)
3. If git enabled, creates `.gitattributes` for consistent line endings
4. TOMLManager creates `pyproject.toml` with either:
   - Git-based versioning (if `--git` flag used): Uses hatch-vcs, dynamic version from git tags
   - Manual versioning (if `--no-git` flag used): Static version "0.1.0", no hatch-vcs dependency
5. DependenciesManager creates `dependencies.py` from template
6. LicenseManager creates LICENSE file
7. ScaffoldingManager creates folder structure (project_name/, tests/, pipelines/, schemas/, utils/) with `__init__.py` files in package folders
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
   - `pipelines/{name}/__init__.py` - Package marker (auto-created)
   - `pipelines/{name}/{name}_runner.py` - Main pipeline orchestrator
   - `pipelines/{name}/config.py` - Pipeline-specific configuration with TableConfig imports
   - `pipelines/{name}/README.md` - Pipeline documentation template
   - `pipelines/{name}/processors/` - Directory for processor classes
   - `pipelines/{name}/tests/` - Integration tests for the pipeline
5. PipelineManager registers pipeline class in package `__init__.py` for top-level imports
6. Updates `__all__` list in `__init__.py` for explicit exports

The `create-processor` command flow:
1. Validates and normalizes both processor name and pipeline name
2. Converts processor name to PascalCase with "Processor" suffix (e.g., `sales-extractor` → `SalesExtractorProcessor`)
3. ProjectContext searches up tree for pypeline project (init=False mode)
4. Verifies pipeline exists at `pipelines/{pipeline_name}/`
5. Creates processor files:
   - `pipelines/{pipeline}/processors/{name}_processor.py` - Processor class with Extract/Transform pattern
   - `pipelines/{pipeline}/processors/tests/test_{name}_processor.py` - Unit test file with pytest fixtures
6. Creates `processors/tests/` subdirectory if it doesn't exist
7. ProcessorManager auto-registers import in `{pipeline}_runner.py`
8. Import statement inserted after existing processor imports (or after last import if first processor)

The `build` command flow:
1. ProjectContext searches up tree for pypeline project (init=False mode)
2. Reads `pyproject.toml` to get project name and version
3. Cleans existing `dist/snowflake/` directory
4. Creates ZIP archive of project files using Python's `zipfile` module
5. Adds files relative to project root (ensuring `pyproject.toml` is at ZIP root level)
6. Excludes build artifacts (.venv, dist, __pycache__, .git, etc.)
7. Verifies `pyproject.toml` is at ZIP root and displays upload instructions

**Critical**: The ZIP must have `pyproject.toml` at root level (not nested in a folder) for Snowflake to properly import the package. The build command ensures this by adding all files relative to the project root. Package structure is `project_name/project_name/` (NOT `project_name/src/project_name/`).

### Template System

Templates are stored in `src/pypeline_cli/templates/`:
- `shared/init/` - Platform-agnostic scaffolding templates:
  - `databases.py.template` - Database configuration (user-editable)
  - `date_parser.py.template` - Date parsing utilities
  - `logger.py.template` - Logger singleton
  - `types.py.template` - Shared types, enums, dataclasses
  - `basic_test.py.template` - Basic test template
  - `.gitignore.template` - Git ignore patterns
  - `README.md.template` - Project README
  - `_init.py.template` - Package __init__.py
- `snowflake/init/` - Snowflake-specific scaffolding templates:
  - `etl.py.template` - ETL singleton (uses Snowpark)
  - `snowflake_utils.py.template` - Snowflake helper functions
  - `decorators.py.template` - Timing and logging decorators (uses Snowflake APIs)
  - `table_cache.py.template` - TableCache for pre-loading (uses Snowpark DataFrame)
  - `credentials.py.example.template` - Snowflake connection parameters
  - `dependencies.py.template` - BASE_DEPENDENCIES with Snowflake packages
- `snowflake/pipelines/` - Snowflake pipeline templates with variable substitution:
  - `runner.py.template` - Pipeline orchestrator with run(), pipeline(), run_processors(), _write_to_snowflake()
  - `config.py.template` - Pipeline configuration with Database, Schema, TableConfig imports
  - `README.md.template` - Pipeline documentation structure
  - `processors_init.py.template` - Processors package marker
  - `tests_init.py.template` - Integration tests package marker
- `snowflake/processors/` - Snowflake processor templates with variable substitution:
  - `processor.py.template` - Processor class with __init__() for Extract, process() for Transform
  - `test_processor.py.template` - pytest unit test template with mocking fixtures
- `licenses/` - 14 different license templates with variable substitution
- `databricks/` - Databricks-specific templates (structure created, to be populated in Phase 2):
  - `init/` - Databricks scaffolding templates (empty)
  - `pipelines/` - Databricks pipeline templates (empty)
  - `processors/` - Databricks processor templates (empty)
- `init/`, `pipelines/`, `processors/` - Legacy directories (empty, will be removed in future task)

**Config.py Platform Support**:
The `config.py` file provides platform-aware template path resolution:
- `Platform` enum defines SNOWFLAKE and DATABRICKS values
- `get_platform_from_toml()` reads platform from pyproject.toml [tool.pypeline] section
- `SHARED_SCAFFOLD_FILES` list contains 8 platform-agnostic templates
- `get_platform_scaffold_files(platform)` returns combined shared + platform-specific templates (13 for Snowflake)
- `INIT_SCAFFOLD_FILES` maintained for backwards compatibility (defaults to Snowflake)
- Path helper functions: `get_platform_init_path()`, `get_platform_pipelines_path()`, `get_platform_processors_path()`, `get_platform_dependencies_template()`

**Template Variable Substitution**:
Pipeline templates use `string.Template` with variables:
- `$class_name` - PascalCase class name with "Pipeline" suffix (e.g., "BeneficiaryClaimsPipeline")
- `$pipeline_name` - Normalized name (e.g., "beneficiary_claims")
- `$project_name` - Project name from ProjectContext for import paths

Processor templates use `string.Template` with variables:
- `$class_name` - PascalCase class name with "Processor" suffix (e.g., "SalesExtractorProcessor")
- `$processor_name` - Normalized name (e.g., "sales_extractor")
- `$pipeline_name` - Normalized pipeline name (e.g., "customer_segmentation")
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
│   │   ├── create_pipeline.py   # pypeline create-pipeline
│   │   ├── create_processor.py  # pypeline create-processor
│   │   └── build.py         # pypeline build
│   ├── core/
│   │   ├── create_project.py     # Orchestrates project creation
│   │   └── managers/             # Manager classes for different concerns
│   │       ├── project_context.py
│   │       ├── toml_manager.py
│   │       ├── dependencies_manager.py
│   │       ├── license_manager.py
│   │       ├── scaffolding_manager.py
│   │       ├── pipeline_manager.py    # Pipeline creation
│   │       ├── processor_manager.py   # Processor creation
│   │       └── git_manager.py
│   ├── templates/
│   │   ├── licenses/             # License templates
│   │   ├── shared/               # Platform-agnostic templates
│   │   │   └── init/             # 8 shared templates (databases.py, logger.py, types.py, etc.)
│   │   ├── snowflake/            # Snowflake-specific templates
│   │   │   ├── init/             # 6 Snowflake init templates (etl.py, snowflake_utils.py, etc.)
│   │   │   ├── pipelines/        # 5 pipeline templates (runner.py, config.py, etc.)
│   │   │   └── processors/       # 2 processor templates (processor.py, test_processor.py)
│   │   ├── databricks/           # Databricks-specific templates
│   │   │   ├── init/             # (empty, to be populated)
│   │   │   ├── pipelines/        # (empty, to be populated)
│   │   │   └── processors/       # (empty, to be populated)
│   │   ├── init/                 # Legacy directory (empty, to be removed in Task 1.3)
│   │   ├── pipelines/            # Legacy directory (empty, to be removed in Task 1.3)
│   │   └── processors/           # Legacy directory (empty, to be removed in Task 1.3)
│   └── utils/
│       ├── dependency_parser.py  # Parse dependency strings
│       ├── valdators.py          # Input validation
│       └── name_converter.py     # Name normalization/conversion
└── tests/                        # Test files
```

## Generated Project Structure

When users run `pypeline init`, the generated project has this structure (NO src/ folder):

```
my_project/                      # Project root
├── pyproject.toml               # Package configuration
├── dependencies.py              # User-editable dependency list
├── LICENSE                      # Project license
├── README.md                    # Project documentation
├── my_project/                  # Package directory (importable)
│   ├── __init__.py             # Package exports
│   ├── _version.py             # Auto-generated version (if using git)
│   ├── pipelines/              # Pipeline orchestrators
│   │   └── example_pipeline/
│   │       ├── example_pipeline_runner.py
│   │       ├── config.py
│   │       ├── README.md
│   │       ├── processors/
│   │       └── tests/
│   ├── schemas/                # Database schemas (user-created)
│   └── utils/                  # Framework utilities
│       ├── databases.py
│       ├── date_parser.py
│       ├── decorators.py
│       ├── etl.py             # ETL singleton
│       ├── logger.py          # Logger singleton
│       ├── snowflake_utils.py
│       ├── table_cache.py     # TableCache for pre-loading
│       └── types.py           # Shared types, enums, dataclasses
└── tests/                      # Integration tests
    └── basic_test.py
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

### Processor Pattern

Processors are created using `pypeline create-processor --name <name> --pipeline <pipeline>`:
- Handle data extraction in `__init__` using TableConfig from `utils/tables.py` or pipeline `config.py`
- Implement `process()` method as orchestrator for transformations
- Use private methods for atomized transformation steps
- Return DataFrames
- Auto-instantiate Logger and ETL utilities
- Use `@time_function` decorator on `process()` method

Generated processor structure:
```python
class SalesExtractorProcessor:
    def __init__(self, month: int):
        self.logger = Logger()
        self.etl = ETL()
        # Extract data using TableConfig
        SALES_TABLE.month = month
        table_name = SALES_TABLE.generate_table_name()
        self.sales_df = self.etl.session.table(table_name)

    @time_function(f"{MODULE_NAME}.process")
    def process(self) -> DataFrame:
        # Orchestrate transformations
        df = self._filter_valid()
        df = self._aggregate(df)
        return df

    def _filter_valid(self) -> DataFrame:
        # Atomized transformation
        return self.sales_df.filter(col("STATUS") == "COMPLETED")

    def _aggregate(self, df: DataFrame) -> DataFrame:
        # Atomized transformation
        return df.group_by("CUSTOMER_ID").agg(sum_("AMOUNT"))
```

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

**Pipelines:**
- **Input**: User provides name (e.g., `beneficiary-claims`, `enrollment`, `CLAIMS`)
- **Normalization**: Convert to lowercase with underscores (e.g., `beneficiary_claims`)
- **Folder/File**: Use normalized name (e.g., `pipelines/beneficiary_claims/beneficiary_claims_runner.py`)
- **Class Name**: PascalCase + "Pipeline" suffix (e.g., `BeneficiaryClaimsPipeline`)
- **Import**: Registered in package `__init__.py` for top-level import

**Processors:**
- **Input**: User provides name (e.g., `sales-extractor`, `msp`, `ENRICHMENT`)
- **Normalization**: Convert to lowercase with underscores (e.g., `sales_extractor`)
- **File**: Use normalized name with `_processor.py` suffix (e.g., `sales_extractor_processor.py`)
- **Class Name**: PascalCase + "Processor" suffix (e.g., `SalesExtractorProcessor`)
- **Import**: Auto-registered in pipeline runner file (e.g., `from .processors.sales_extractor_processor import SalesExtractorProcessor`)

Handled by `utils/name_converter.py`:
- `normalize_name()` - Strips whitespace, lowercases, converts hyphens to underscores
- `to_pascal_case()` - Converts normalized name to PascalCase
- Commands add appropriate suffix ("Pipeline" or "Processor") to class name

## Key Conventions

- **Path handling**: Use `pathlib.Path` throughout, never string concatenation
- **Click output**: Use `click.echo()` for all user-facing messages, not `print()`
- **Template naming**: Templates end with `.template` extension
- **Manager initialization**: All managers receive `ProjectContext` instance
- **Version management**: Projects use hatch-vcs for git tag-based versioning
- **Class naming**:
  - Pipeline classes always have "Pipeline" suffix (e.g., `BeneficiaryClaimsPipeline`)
  - Processor classes always have "Processor" suffix (e.g., `SalesExtractorProcessor`)
- **ETL Pattern**:
  - Extract happens in processor `__init__()` method
  - Transform happens in processor `process()` method
  - Load happens in pipeline `_write_to_snowflake()` method
- **Framework vs User Code**:
  - Framework files (etl.py, logger.py, decorators.py, table_cache.py, snowflake_utils.py, types.py) marked "DO NOT MODIFY"
  - User-editable files (databases.py, dependencies.py) clearly documented
  - Generated scaffolding (runners, processors) includes TODO comments for implementation

## Key Utility Functions

### types.py - Shared Types and Dataclasses

**File:** `utils/types.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Centralized location for all shared types, enums, and dataclasses used across the framework.

**Key Components:**

#### `LogLevel` Enum
Defines log levels with color coding for terminal output:
- `DEBUG` (10): Gray - Detailed diagnostic information
- `INFO` (20): Green - General informational messages
- `WARN` (30): Yellow - Warning messages
- `ERROR` (40): Red - Error messages
- `CRITICAL` (50): Magenta - Critical failures

#### `TableConfig` Dataclass
Configuration for dynamic table naming with temporal partitioning:

```python
from ...utils.types import TableConfig

# Yearly table
config = TableConfig(
    database="ANALYTICS",
    schema="RAW",
    table_name_template="sales_{YYYY}",
    type="YEARLY",
    is_output=False
)
config.generate_table_name(year=2025)  # "ANALYTICS.RAW.sales_2025"

# Monthly table
config = TableConfig(
    database="PROD",
    schema="STAGING",
    table_name_template="events_{MM}",
    type="MONTHLY",
    month=3,
    is_output=False
)
config.generate_table_name()  # "PROD.STAGING.events_03"

# Stable table
config = TableConfig(
    database="ANALYTICS",
    schema="REPORTING",
    table_name_template="dim_products",
    type="STABLE",
    is_output=True  # Marks as output table (not pre-loaded into cache)
)
config.generate_table_name()  # "ANALYTICS.REPORTING.dim_products"
```

**Methods:**
- `generate_table_name(year: Optional[int] = None) -> str`: Returns fully qualified table name
- `generate_parsed_table_path(year: Optional[int] = None) -> Dict`: Returns dict with `database`, `schema`, `table` keys

**Template Placeholders:**
- `{YYYY}` - 4-digit year (e.g., 2025)
- `{YY}` - 2-digit year (e.g., 25)
- `{MM}` - 2-digit month with leading zero (e.g., 01, 12)

#### `ParsedTablePath` Dataclass
Represents a decomposed table path with database, schema, and table components:

```python
@dataclass
class ParsedTablePath:
    database: str
    schema: str
    table: str

    @property
    def full_name(self) -> str:
        return f"{self.database}.{self.schema}.{self.table}"
```

#### `TimestampResult` TypedDict
Return type for timestamp queries:
- `dt`: timezone-aware datetime object
- `iso`: ISO 8601 formatted string

#### `ParsedDateTime` TypedDict
Validated datetime with UTC normalization for date parsing utilities.

### snowflake_utils.py - Snowflake Helper Functions

**File:** `utils/snowflake_utils.py` (⚙️ Framework - Do Not Modify)

**Purpose:** Provides Snowflake-specific helper functions that integrate with TableConfig for common operations.

**Key Functions:**

#### `get_table_last_modified()`

Get the last modified timestamp for a table in Eastern timezone.

```python
from ...utils.snowflake_utils import get_table_last_modified
from ...utils.etl import ETL

etl = ETL()

# Using TableConfig (preferred)
result = get_table_last_modified(
    etl.session,
    config=SALES_TABLE,
    year=2025
)
print(result["iso"])  # '2025-01-15T14:30:00-05:00'
print(result["dt"])   # datetime object in America/New_York

# Using explicit path
result = get_table_last_modified(
    etl.session,
    database_name="ANALYTICS",
    schema_name="RAW",
    table_name="sales_2025"
)
```

**Parameters:**
- `session`: Active Snowpark Session
- `config`: Optional TableConfig (preferred)
- `year`: Optional year for TableConfig resolution
- `database_name`, `schema_name`, `table_name`: Alternative explicit path

**Returns:** `TimestampResult` dict with `dt` (datetime) and `iso` (string) keys

#### `check_table_exists()`

Check if a table exists in Snowflake. Returns False on permission errors.

```python
from ...utils.snowflake_utils import check_table_exists

# Using TableConfig
exists = check_table_exists(etl.session, config=SALES_TABLE, year=2025)

# Using explicit path
exists = check_table_exists(
    etl.session,
    database_name="PROD",
    schema_name="ANALYTICS",
    table_name="customer_segments"
)

if exists:
    logger.info("Table found")
```

**Returns:** `True` if table exists, `False` otherwise (including on permission errors)

#### `check_table_read_access()`

Verify read permissions by attempting a minimal read operation (SELECT 1 LIMIT 1).

```python
from ...utils.snowflake_utils import check_table_read_access

# Check if we can read from the table
can_read = check_table_read_access(
    etl.session,
    config=ORDERS_TABLE,
    year=2025
)

if can_read:
    # Safe to proceed with data extraction
    df = etl.session.table(ORDERS_TABLE.generate_table_name(year=2025))
else:
    logger.error("No read access to orders table")
```

**Returns:** `True` if read succeeds, `False` if table doesn't exist or is inaccessible

#### `parse_table_path()`

Internal helper that resolves table paths from either TableConfig or explicit components.

```python
from ...utils.snowflake_utils import parse_table_path

# From TableConfig
path = parse_table_path(config=SALES_TABLE, year=2025)
print(path.database)   # "ANALYTICS"
print(path.schema)     # "RAW"
print(path.table)      # "sales_2025"
print(path.full_name)  # "ANALYTICS.RAW.sales_2025"

# From explicit parts
path = parse_table_path(
    database_name="PROD",
    schema_name="DIM",
    table_name="customers"
)
```

**Returns:** `ParsedTablePath` with `database`, `schema`, `table`, and `full_name` attributes

**Best Practices:**
- Prefer using TableConfig parameter over explicit paths for consistency
- Use `check_table_exists()` before operations that assume table presence
- Use `check_table_read_access()` to verify permissions before data extraction
- Use `get_table_last_modified()` for freshness checks and monitoring
- All functions handle errors gracefully and log warnings/errors appropriately

**Common Use Cases:**
- Pre-flight checks in pipeline `__init__()` to validate table availability
- Permission verification before attempting data extraction
- Freshness monitoring for data quality and staleness detection
- Dynamic table discovery with TableConfig integration
- Error handling for missing or inaccessible tables
