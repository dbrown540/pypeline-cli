# Multi-Platform Support Refactoring Plan for pypeline-cli

## Overview

Refactor pypeline-cli to support both **Snowflake (Snowpark)** and **Databricks (PySpark)** platforms. 

## User Requirements Summary

1. **Platform Selection**: `--platform snowflake|databricks`
2. **Databricks Target**: Unity Catalog with Delta tables (`spark.table("catalog.schema.table")`)
3. **Databricks Auth**: `DatabricksSession.builder.getOrCreate()` with credentials file fallback
   - Credentials file contains: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_CLUSTER_ID`
4. **Template Organization**: Shared directory for pure Python files, platform directories for specific implementations
5. **Project Independence**: Generated projects remain standalone (no upgrade command)
6. **No Backwards Compatibility**: Current release is unstable, breaking changes acceptable

---

## Architecture Overview

### Template Directory Structure

```
templates/
├── shared/                          # Pure Python, no platform dependencies
│   └── init/
│       ├── databases.py.template
│       ├── date_parser.py.template
│       ├── logger.py.template
│       ├── types.py.template        # Platform-agnostic version
│       ├── basic_test.py.template
│       ├── .gitignore.template
│       ├── README.md.template
│       └── _init.py.template
│
├── snowflake/                       # Snowpark-specific templates
│   ├── init/
│   │   ├── etl.py.template
│   │   ├── snowflake_utils.py.template
│   │   ├── decorators.py.template
│   │   ├── table_cache.py.template
│   │   ├── dependencies.py.template
│   │   └── credentials.py.example.template
│   ├── pipelines/
│   │   ├── runner.py.template
│   │   ├── config.py.template
│   │   ├── README.md.template
│   │   ├── processors_init.py.template
│   │   └── tests_init.py.template
│   └── processors/
│       ├── processor.py.template
│       └── test_processor.py.template
│
├── databricks/                      # PySpark-specific templates
│   ├── init/
│   │   ├── etl.py.template
│   │   ├── databricks_utils.py.template
│   │   ├── decorators.py.template
│   │   ├── table_cache.py.template
│   │   ├── dependencies.py.template
│   │   └── credentials.py.example.template
│   ├── pipelines/
│   │   ├── runner.py.template
│   │   ├── config.py.template
│   │   ├── README.md.template
│   │   ├── processors_init.py.template
│   │   └── tests_init.py.template
│   └── processors/
│       ├── processor.py.template
│       └── test_processor.py.template
│
└── licenses/                        # Shared (unchanged)
```

### Key Design Principles

1. **Config-Driven**: Platform determines dependencies and template paths via `config.py` global `PLATFORM` variable
2. **Context-Aware**: `ProjectContext` reads platform from `pyproject.toml` and managers use it automatically
3. **TOML-First**: Platform stored in `pyproject.toml` `[tool.pypeline]` section, read via helper function
4. **Extensible**: Architecture supports adding new platforms in the future

---

## Implementation Plan

### PHASE 1: Foundation Setup (No User Impact)

#### Task 1.1: Create Template Directory Structure
**Files**: `src/pypeline_cli/templates/`

**Actions**:
1. Create new directory structure:
   ```
   mkdir -p templates/shared/init
   mkdir -p templates/snowflake/init
   mkdir -p templates/snowflake/pipelines
   mkdir -p templates/snowflake/processors
   mkdir -p templates/databricks/init
   mkdir -p templates/databricks/pipelines
   mkdir -p templates/databricks/processors
   ```

2. Move existing templates:
   - Move `templates/init/` → `templates/snowflake/init/` (platform-specific files)
   - Copy shared files to `templates/shared/init/`
   - Move `templates/pipelines/` → `templates/snowflake/pipelines/`
   - Move `templates/processors/` → `templates/snowflake/processors/`
   - Keep `templates/licenses/` at root (unchanged)

**Shared files** (no platform deps):
- `databases.py.template`
- `date_parser.py.template`
- `logger.py.template`
- `types.py.template` (already platform-agnostic)
- `basic_test.py.template`
- `.gitignore.template`
- `README.md.template`
- `_init.py.template`

**Platform-specific files** (Snowflake and Databricks):
- `etl.py.template`
- `*_utils.py.template` (snowflake_utils.py or databricks_utils.py)
- `decorators.py.template`
- `table_cache.py.template`
- `dependencies.py.template` (platform-specific BASE_DEPENDENCIES)
- `credentials.py.example.template` (platform-specific auth configs)

**Verification**: Run existing tests to ensure templates still load correctly from new paths.

---

#### Task 1.2: Move Platform-Specific Templates
**Files**:
- `templates/snowflake/init/dependencies.py.template`
- `templates/snowflake/init/credentials.py.example.template`
- `templates/databricks/init/dependencies.py.template`
- `templates/databricks/init/credentials.py.example.template`

**Actions**:
1. **Move** `dependencies.py.template` from `shared/` to both `snowflake/init/` and `databricks/init/`
2. **Move** `credentials.py.example.template` from `shared/` to both `snowflake/init/` and `databricks/init/`
3. **Update Snowflake `dependencies.py.template`**:
   - Set `BASE_DEPENDENCIES = ["snowflake-snowpark-python>=1.42.0", ...]`
4. **Create Databricks `dependencies.py.template`**:
   - Set `BASE_DEPENDENCIES = ["pyspark>=3.5.0", "delta-spark>=3.0.0", ...]`
5. **Update Snowflake `credentials.py.example.template`**: Keep existing Snowflake connection params
6. **Create Databricks `credentials.py.example.template`**:
   ```python
   DATABRICKS_HOST = "https://adb-xxx.azuredatabricks.net"
   DATABRICKS_TOKEN = "your-personal-access-token"
   DATABRICKS_CLUSTER_ID = "your-cluster-id"
   ```

**Verification**: Both platforms have their own dependencies and credentials templates.

---

#### Task 1.3: Update config.py with Platform Support
**File**: `src/pypeline_cli/config.py`

**Strategy**: Use a global `PLATFORM` variable derived from a helper function that reads `pyproject.toml`. This simplifies all path definitions to use dynamic platform resolution.

**Changes**:

1. **Add Platform enum and helper function**:
   ```python
   from enum import Enum
   import tomllib
   from pathlib import Path

   class Platform(str, Enum):
       """Supported platforms for pypeline projects."""
       SNOWFLAKE = "snowflake"
       DATABRICKS = "databricks"

   def get_platform_from_toml(toml_path: Path | None = None) -> str | None:
       """
       Read platform from pyproject.toml.

       Searches for pyproject.toml in current directory or parents.
       Returns None if no pypeline project found (user hasn't run init yet).

       Note: Since users must run 'pypeline init' before any other command,
       and init creates pyproject.toml first, this will always find a platform
       for valid pypeline projects.
       """
       if toml_path is None:
           # Try to find pyproject.toml in current directory or parents
           current = Path.cwd()
           for parent in [current] + list(current.parents):
               candidate = parent / "pyproject.toml"
               if candidate.exists():
                   toml_path = candidate
                   break

       if toml_path is None or not toml_path.exists():
           return None  # No pypeline project found

       try:
           with open(toml_path, "rb") as f:
               data = tomllib.load(f)
           platform = data.get("tool", {}).get("pypeline", {}).get("platform")
           if platform is None:
               raise ValueError(
                   "Platform not set in pyproject.toml [tool.pypeline]. "
                   "This pypeline project may be corrupted. "
                   "Add 'platform = \"snowflake\"' or 'platform = \"databricks\"'."
               )
           return platform
       except Exception as e:
           raise ValueError(f"Failed to read platform from {toml_path}: {e}")

   # Global platform variable
   # Will be None only when run outside a pypeline project (before init)
   # All pypeline commands after init will have this set
   PLATFORM = get_platform_from_toml()
   ```

2. **Simplify template paths using PLATFORM**:
   ```python
   PATH_TO_TEMPLATES = Path(__file__).parent / "templates"
   PATH_TO_SHARED_INIT = PATH_TO_TEMPLATES / "shared" / "init"
   PATH_TO_LICENSES = PATH_TO_TEMPLATES / "licenses"

   # Platform-specific paths (dynamic based on PLATFORM)
   def get_platform_init_path(platform: str) -> Path:
       return PATH_TO_TEMPLATES / platform / "init"

   def get_platform_pipelines_path(platform: str) -> Path:
       return PATH_TO_TEMPLATES / platform / "pipelines"

   def get_platform_processors_path(platform: str) -> Path:
       return PATH_TO_TEMPLATES / platform / "processors"

   # Convenience shortcuts for current platform
   PATH_TO_INIT = get_platform_init_path(PLATFORM) if PLATFORM else None
   PATH_TO_PIPELINES = get_platform_pipelines_path(PLATFORM) if PLATFORM else None
   PATH_TO_PROCESSORS = get_platform_processors_path(PLATFORM) if PLATFORM else None
   ```

3. **Simplify scaffold file lists**:
   ```python
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
       """Get platform-specific scaffold files dynamically."""
       platform_init_path = get_platform_init_path(platform)

       platform_files = [
           ScaffoldFile(
               template_name=platform_init_path / "etl.py.template",
               destination_property="etl_file",
           ),
           ScaffoldFile(
               template_name=platform_init_path / f"{platform}_utils.py.template",
               destination_property="platform_utils_file",
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
               template_name=platform_init_path / "dependencies.py.template",
               destination_property="dependencies_path",
           ),
           ScaffoldFile(
               template_name=platform_init_path / "credentials.py.example.template",
               destination_property="credentials_example_file",
           ),
       ]

       return SHARED_SCAFFOLD_FILES + platform_files
   ```

4. **Remove `DEFAULT_DEPENDENCIES`**: No longer needed since dependencies are defined per-platform in their respective `dependencies.py.template` files.

**Key Insight**:
Since `pypeline init` creates `pyproject.toml` **first** (before any templates or other files), the global `PLATFORM` variable will always be available for all pypeline commands. The only time `PLATFORM` is `None` is when running outside a pypeline project (before init is run), which is the expected behavior.

**Verification**:
- Import config.py from outside a pypeline project - verify `PLATFORM = None`
- Run `pypeline init` and verify `pyproject.toml` is created with platform field
- Import config.py from within the new project - verify `PLATFORM` is set correctly
- Verify `get_platform_scaffold_files()` returns correct file lists for both platforms

---

### PHASE 2: Databricks Template Creation

#### Task 2.1: Create Databricks etl.py Template
**File**: `templates/databricks/init/etl.py.template`

**Implementation**:
```python
"""
Auto-generated ETL singleton for Databricks Spark session management.

⚙️ Framework File - Do Not Modify
"""

from databricks.connect import DatabricksSession
from .logger import Logger

# Check if credentials file exists
try:
    from .credentials import DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_CLUSTER_ID
    _credentials_available = True
except ImportError:
    _credentials_available = False


class ETL:
    """
    Singleton ETL class for Databricks Spark session management.

    Connection Strategy:
        1. Try DatabricksSession.builder.getOrCreate() (Databricks workspace)
        2. Fall back to credentials.py if available
        3. Automatically connects to Unity Catalog

    Usage:
        etl = ETL()
        df = etl.session.table("catalog.schema.table")
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_session()
        return cls._instance

    def _initialize_session(self):
        """Initialize Databricks session with workspace or credentials fallback."""
        logger = Logger()

        try:
            # Try workspace session first
            self._session = (
                DatabricksSession.builder
                .appName("pypeline")
                .getOrCreate()
            )
            logger.info(
                message="Databricks session initialized (workspace)",
                context="utils.etl"
            )
        except Exception as e:
            # Fall back to credentials file if available
            if _credentials_available:
                logger.warn(
                    message="Workspace session failed, using credentials.py",
                    context="utils.etl"
                )
                self._session = (
                    DatabricksSession.builder
                    .host(DATABRICKS_HOST)
                    .token(DATABRICKS_TOKEN)
                    .clusterId(DATABRICKS_CLUSTER_ID)
                    .getOrCreate()
                )
                logger.info(
                    message="Databricks session initialized (credentials)",
                    context="utils.etl"
                )
            else:
                raise RuntimeError(
                    "No Databricks session available. "
                    "Either run in workspace or create credentials.py"
                ) from e

    @property
    def session(self) -> DatabricksSession:
        return self._session
```

**Key Differences from Snowpark**:
- Uses `DatabricksSession` instead of Snowpark `Session`
- Uses `getOrCreate()` with `.host()`, `.token()`, `.clusterId()` for credentials
- Dual connection strategy: workspace first, then credentials fallback
- Type hint: `DatabricksSession` instead of `Session`

---

#### Task 2.2: Create Databricks databricks_utils.py Template
**File**: `templates/databricks/init/databricks_utils.py.template`

**Implementation**:
```python
"""
Auto-generated Databricks utility helpers.

⚙️ Framework File - Do Not Modify
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from pyspark.sql import SparkSession

from .logger import Logger
from .types import TableConfig, TimestampResult, ParsedTablePath


def get_table_last_modified(
    session: SparkSession,
    config: TableConfig | None = None,
    year: int | None = None,
    catalog_name: str | None = None,
    schema_name: str | None = None,
    table_name: str | None = None,
) -> TimestampResult:
    """
    Return the last modified timestamp for a Delta table in Eastern time.

    Args:
        session: Active SparkSession
        config: Optional TableConfig (preferred)
        year: Optional year for TableConfig resolution
        catalog_name: Unity Catalog name
        schema_name: Schema name
        table_name: Table name

    Returns:
        TimestampResult with dt and iso keys
    """
    path = parse_table_path(config, year, catalog_name, schema_name, table_name)

    # Query Unity Catalog INFORMATION_SCHEMA
    query = f"""
        SELECT table_catalog, table_schema, table_name, last_altered
        FROM system.information_schema.tables
        WHERE table_catalog = '{path.database}'
          AND table_schema = '{path.schema}'
          AND table_name = '{path.table}'
    """

    result = session.sql(query).collect()

    if not result:
        raise ValueError(f"Table not found: {path.full_name}")

    # Convert to Eastern timezone
    utc_time = result[0]["last_altered"]
    eastern = utc_time.astimezone(ZoneInfo("America/New_York"))

    return {
        "dt": eastern,
        "iso": eastern.isoformat()
    }


def check_table_exists(
    session: SparkSession,
    config: TableConfig | None = None,
    year: int | None = None,
    catalog_name: str | None = None,
    schema_name: str | None = None,
    table_name: str | None = None,
) -> bool:
    """
    Check if a table exists in Unity Catalog.

    Returns False on permission errors.
    """
    path = parse_table_path(config, year, catalog_name, schema_name, table_name)

    try:
        return session.catalog.tableExists(path.full_name)
    except Exception as e:
        logger = Logger()
        logger.warn(
            message=f"Error checking table existence: {e}",
            context="databricks_utils.check_table_exists"
        )
        return False


def check_table_read_access(
    session: SparkSession,
    config: TableConfig | None = None,
    year: int | None = None,
    catalog_name: str | None = None,
    schema_name: str | None = None,
    table_name: str | None = None,
) -> bool:
    """Verify read permissions by attempting a minimal read."""
    path = parse_table_path(config, year, catalog_name, schema_name, table_name)

    try:
        session.sql(f"SELECT 1 FROM {path.full_name} LIMIT 1").collect()
        return True
    except Exception:
        return False


def parse_table_path(
    config: TableConfig | None = None,
    year: int | None = None,
    catalog_name: str | None = None,
    schema_name: str | None = None,
    table_name: str | None = None,
) -> ParsedTablePath:
    """
    Parse table path from TableConfig or explicit parameters.

    For Databricks, returns ParsedTablePath with catalog, schema, table.
    Note: 'database' field in ParsedTablePath maps to Unity Catalog name.
    """
    if config:
        parsed = config.generate_parsed_table_path(year=year)
        return ParsedTablePath(
            database=parsed["data"]["database"],  # Maps to catalog
            schema=parsed["data"]["schema"],
            table=parsed["data"]["table"]
        )
    elif all([catalog_name, schema_name, table_name]):
        return ParsedTablePath(
            database=catalog_name,
            schema=schema_name,
            table=table_name
        )
    else:
        raise ValueError(
            "Must provide either config or all of catalog/schema/table names"
        )
```

**Key Differences from snowflake_utils.py**:
- Uses `system.information_schema.tables` (Unity Catalog)
- Uses `session.catalog.tableExists()` directly
- Same function signatures for consistency
- Comments reference Unity Catalog and Delta tables

---

#### Task 2.3: Create Databricks decorators.py Template
**File**: `templates/databricks/init/decorators.py.template`

**Implementation**: Similar structure to Snowflake version with these changes:
- Replace `session.catalog.table_exists()` with `session.catalog.tableExists()`
- For `@skip_if_updated_this_month()`: Query `system.information_schema.tables` instead of using `SYSTEM$LAST_CHANGE_COMMIT_TIME()`
- Keep `@time_function()` unchanged (pure Python)

---

#### Task 2.4: Create Databricks table_cache.py Template
**File**: `templates/databricks/init/table_cache.py.template`

**Implementation**: Near-identical to Snowflake version with these changes:
- Import: `from pyspark.sql import DataFrame` instead of `from snowflake.snowpark import DataFrame`
- Table loading: `self.etl.session.table(table_name)` works the same (Unity Catalog aware)

---

#### Task 2.5: Create Databricks Pipeline Templates
**File**: `templates/databricks/pipelines/runner.py.template`

**Key Changes**:
- Import: `from pyspark.sql import DataFrame`
- Write method renamed: `_write_to_databricks()` instead of `_write_to_snowflake()`
- Write operation:
  ```python
  df.write.format("delta").mode(write_mode).saveAsTable(table_path)
  ```

**Other templates**:
- `config.py.template`: Same as Snowflake (uses TableConfig)
- `README.md.template`: Update references to "Databricks" and "Unity Catalog"
- `processors_init.py.template`: Same as Snowflake
- `tests_init.py.template`: Same as Snowflake

---

#### Task 2.6: Create Databricks Processor Templates
**File**: `templates/databricks/processors/processor.py.template`

**Key Changes**:
- Import: `from pyspark.sql import DataFrame`
- Import: `from pyspark.sql.functions import col` (instead of `snowflake.snowpark.functions`)
- Rest of logic remains identical (APIs are compatible)

**File**: `templates/databricks/processors/test_processor.py.template`

Same as Snowflake version (pytest patterns are platform-agnostic).

---

### PHASE 3: Core Manager Refactoring

#### Task 3.1: Update ProjectContext with Platform Property
**File**: `src/pypeline_cli/core/managers/project_context.py`

**Changes**:

1. **Add platform property** (uses same logic as `config.get_platform_from_toml()`):
   ```python
   @property
   def platform(self) -> str:
       """
       Get platform from pyproject.toml.

       Raises ValueError if platform not set.
       """
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
       except FileNotFoundError:
           raise ValueError(f"pyproject.toml not found at {self.toml_path}")
   ```

2. **Add generic platform_utils_file property**:
   ```python
   @property
   def platform_utils_file(self) -> Path:
       """
       Get platform-specific utils file path.

       Returns snowflake_utils.py for snowflake, databricks_utils.py for databricks.
       """
       platform = self.platform
       return self.project_utils_folder_path / f"{platform}_utils.py"
   ```

3. **Remove or update snowflake_utils_file property**:
   - Option A: Keep it as alias to `platform_utils_file` for compatibility
   - Option B: Remove it entirely (breaking change acceptable)
   - **Recommendation**: Remove it to enforce new pattern

**Verification**:
- Test that platform property raises clear error if platform not set
- Test that platform_utils_file returns correct path for both platforms

---

#### Task 3.2: Update TOMLManager to Store Platform
**File**: `src/pypeline_cli/core/managers/toml_manager.py`

**Changes**:

1. **Add platform parameter to create()**:
   ```python
   def create(
       self,
       name: str,
       author_name: str,
       author_email: str,
       description: str,
       license: str,
       platform: str,  # NEW PARAMETER
       use_git: bool = False,
   ):
   ```

2. **Remove platform-specific dependencies from pyproject.toml**:
   - Dependencies are now defined in platform-specific `dependencies.py.template`
   - User will manage them via `dependencies.py` → `pypeline sync-deps`
   - Initial `pyproject.toml` should have minimal/empty dependencies list

3. **Store platform in [tool.pypeline]**:
   ```python
   "tool": {
       "pypeline": {
           "managed": True,
           "platform": platform,  # NEW FIELD
       },
       # ... rest of tool config
   }
   ```

**Verification**:
- Create test project and verify platform field in pyproject.toml
- Verify dependencies list is empty or minimal
- Verify platform can be read by `config.get_platform_from_toml()`

---

#### Task 3.3: Update PipelineManager with Platform Awareness
**File**: `src/pypeline_cli/core/managers/pipeline_manager.py`

**Changes**:

1. **Read platform from context in __init__()**:
   ```python
   def __init__(self, ctx: ProjectContext) -> None:
       self.ctx = ctx
       self.platform = ctx.platform

       from ...config import get_platform_pipelines_path
       self.templates_path = get_platform_pipelines_path(self.platform)
   ```

**No other changes needed** - template substitution logic is platform-agnostic.

**Verification**: Verify correct template directory is selected based on platform.

---

#### Task 3.4: Update ProcessorManager with Platform Awareness
**File**: `src/pypeline_cli/core/managers/processor_manager.py`

**Changes**:

1. **Read platform from context in __init__()**:
   ```python
   def __init__(self, ctx: ProjectContext) -> None:
       self.ctx = ctx
       self.platform = ctx.platform

       from ...config import get_platform_processors_path
       self.templates_path = get_platform_processors_path(self.platform)
   ```

**No other changes needed**.

**Verification**: Verify correct template directory is selected.

---

### PHASE 4: Command Updates

#### Task 4.1: Update init Command with --platform Flag
**File**: `src/pypeline_cli/commands/init.py`

**Changes**:

1. **Add --platform option**:
   ```python
   @click.option(
       "--platform",
       type=click.Choice(["snowflake", "databricks"], case_sensitive=False),
       prompt="Select target platform",
       default="snowflake",
       help="Target platform for the pipeline (snowflake or databricks)",
       show_choices=True,
   )
   def init(
       destination: str,
       name: str,
       author_name: str,
       author_email: str,
       description: str,
       license: str,
       company_name: str,
       git: bool,
       platform: str,  # NEW PARAMETER
   ):
   ```

2. **Pass platform to create_project()**:
   ```python
   create_project(
       ctx=ctx,
       name=name,
       author_name=author_name,
       author_email=author_email,
       description=description,
       license=license,
       company_name=company_name,
       path=path,
       use_git=git,
       platform=platform,  # NEW PARAMETER
   )
   ```

3. **Update success message**:
   ```python
   click.echo(f"\n✅ Successfully created {platform} project '{name}'!")
   ```

**Verification**: Run `pypeline init --help` and verify --platform option appears.

---

#### Task 4.2: Update create_project() with Platform Support
**File**: `src/pypeline_cli/core/create_project.py`

**Changes**:

1. **Add platform parameter**:
   ```python
   def create_project(
       ctx: ProjectContext,
       name: str,
       author_name: str,
       author_email: str,
       description: str,
       license: str,
       company_name: str,
       path: Path,
       use_git: bool = False,
       platform: str,  # NEW PARAMETER (required, no default)
   ):
   ```

2. **Pass platform to TOMLManager.create()**:
   ```python
   toml_manager.create(
       name=name,
       author_name=author_name,
       author_email=author_email,
       description=description,
       license=license,
       platform=platform,  # NEW PARAMETER
       use_git=use_git,
   )
   ```

3. **Use platform-specific scaffold files**:
   ```python
   from ..config import get_platform_scaffold_files

   scaffold_files = get_platform_scaffold_files(platform)
   scaffolding_manager.create_files_from_templates(scaffold_files=scaffold_files)
   ```

**Verification**: Create both Snowflake and Databricks projects and verify correct templates are used.

---

#### Task 4.3: Update sync-deps Command (No Changes Needed)
**File**: `src/pypeline_cli/commands/sync_deps.py`

**Analysis**:
- sync-deps reads dependencies from `dependencies.py` (which is now platform-specific)
- Dependencies are synced to `pyproject.toml`
- No platform migration needed since we're not supporting backwards compatibility
- If platform is missing from pyproject.toml, `ProjectContext.platform` will raise a clear error

**Verification**: Run sync-deps and verify it works correctly with platform-specific dependencies.

---

### PHASE 5: Testing & Validation

#### Task 5.1: Create Test Projects
**Actions**:

1. **Create Snowflake project**:
   ```bash
   pypeline init \
     --destination ./test-snowflake \
     --name test-snowflake \
     --platform snowflake
   ```

2. **Create Databricks project**:
   ```bash
   pypeline init \
     --destination ./test-databricks \
     --name test-databricks \
     --platform databricks
   ```

3. **Verify file structure**:
   - Snowflake: `utils/snowflake_utils.py` exists
   - Databricks: `utils/databricks_utils.py` exists
   - Both: Correct imports in etl.py, runner templates

4. **Create pipeline in each**:
   ```bash
   cd test-snowflake && pypeline create-pipeline --name test-pipeline
   cd test-databricks && pypeline create-pipeline --name test-pipeline
   ```

5. **Create processor in each**:
   ```bash
   pypeline create-processor --name test-processor --pipeline test-pipeline
   ```

6. **Verify templates**:
   - Snowflake: Uses `snowflake.snowpark` imports
   - Databricks: Uses `pyspark.sql` imports

---

#### Task 5.2: Test Error Handling
**Actions**:

1. **Test missing platform field**:
   - Manually remove platform field from pyproject.toml
   - Run `pypeline create-pipeline` or `pypeline sync-deps`
   - Verify clear error message is displayed:
     ```
     Platform not set in pyproject.toml.
     Add 'platform = "snowflake"' or 'platform = "databricks"'
     to [tool.pypeline] section.
     ```

2. **Test invalid platform value**:
   - Set `platform = "invalid"` in pyproject.toml
   - Verify appropriate error message

---

### PHASE 6: Documentation Updates

#### Task 6.1: Update CLAUDE.md
**File**: `CLAUDE.md`

**Sections to Add**:

1. **Platform Support**:
   ```markdown
   ## Platform Support

   pypeline-cli supports two platforms:
   - **Snowflake**: Uses Snowpark for DataFrame operations
   - **Databricks**: Uses PySpark with Unity Catalog and Delta tables

   Platform is selected during `pypeline init` via the `--platform` flag.
   ```

2. **Platform-Specific Templates**:
   ```markdown
   ### Template Organization

   Templates are organized by platform:
   - `templates/shared/` - Pure Python files (no platform dependencies)
   - `templates/snowflake/` - Snowpark-specific implementations
   - `templates/databricks/` - PySpark-specific implementations
   - `templates/licenses/` - License templates (shared)
   ```

3. **Platform Selection**:
   ```markdown
   ### Platform Selection

   During init:
   ```bash
   pypeline init --platform snowflake  # or databricks
   ```

   Platform is stored in `pyproject.toml`:
   ```toml
   [tool.pypeline]
   managed = true
   platform = "snowflake"  # or "databricks"
   ```
   ```

4. **Update Architecture section** with new config.py structure.

---

#### Task 6.2: Update README (if exists)
**File**: `README.md`

**Add platform examples**:
```markdown
## Getting Started

Create a new pipeline project:

```bash
# Snowflake project
pypeline init --platform snowflake --name my-snowflake-pipeline

# Databricks project
pypeline init --platform databricks --name my-databricks-pipeline
```
```

---

## Critical Files Reference

### Configuration
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/config.py` - Platform mappings, dependencies, template paths

### Managers
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/core/managers/project_context.py` - Platform detection
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/core/managers/toml_manager.py` - Platform storage
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/core/managers/pipeline_manager.py` - Platform-aware templates
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/core/managers/processor_manager.py` - Platform-aware templates

### Commands
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/commands/init.py` - Platform selection
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/commands/sync_deps.py` - Platform migration
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/core/create_project.py` - Orchestration

### Templates (New Structure)
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/templates/shared/` - Platform-agnostic
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/templates/snowflake/` - Snowpark
- `/private/var/folders/.../pypeline-cli/src/pypeline_cli/templates/databricks/` - PySpark

---

## Implementation Sequence

```
Phase 1: Foundation
├── 1.1: Create directory structure
├── 1.2: Make types.py platform-agnostic
└── 1.3: Update config.py

Phase 2: Databricks Templates
├── 2.1: etl.py
├── 2.2: databricks_utils.py
├── 2.3: decorators.py
├── 2.4: table_cache.py
├── 2.5: Pipeline templates
└── 2.6: Processor templates

Phase 3: Manager Refactoring
├── 3.1: ProjectContext
├── 3.2: TOMLManager
├── 3.3: PipelineManager
└── 3.4: ProcessorManager

Phase 4: Commands
├── 4.1: init command
├── 4.2: create_project()
└── 4.3: sync-deps command

Phase 5: Testing
├── 5.1: Create test projects
└── 5.2: Backwards compatibility

Phase 6: Documentation
├── 6.1: Update CLAUDE.md
└── 6.2: Update README
```

---

## Breaking Changes

**Yes** - This release introduces breaking changes:
1. **Platform field required**: All pypeline projects must have `platform` set in `[tool.pypeline]`
2. **No automatic migration**: Existing projects must manually add platform field
3. **Dependencies structure**: `dependencies.py` now platform-specific with `BASE_DEPENDENCIES`
4. **Credentials structure**: `credentials.py.example` now platform-specific
5. **Utils file naming**: `platform_utils_file` replaces `snowflake_utils_file` property

**Migration Path for Existing Projects**:
Users must manually add to their `pyproject.toml`:
```toml
[tool.pypeline]
managed = true
platform = "snowflake"  # Add this line
```

---

## Future Extensibility

The architecture supports adding new platforms with minimal code changes. The `PLATFORM` global and helper functions in `config.py` make template paths dynamic, so adding a new platform only requires:

1. Create `templates/<new-platform>/` directory structure
2. Add platform-specific templates (init/, pipelines/, processors/)
3. Add `Platform.NEW_PLATFORM = "new-platform"` to config.py enum
4. Update init command `--platform` choices
5. Create platform-specific `dependencies.py.template` and `credentials.py.example.template`

No manager code changes needed - the architecture is fully extensible.
