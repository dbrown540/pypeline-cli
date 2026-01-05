# KANBAN: Multi-Platform Support Refactoring

## Summary

**Total Tasks:** 20 tasks across 6 phases
**Estimated Complexity:** Major refactoring with breaking changes
**Goal:** Refactor pypeline-cli to support both Snowflake (Snowpark) and Databricks (PySpark) platforms

## Dependency Graph

```
PHASE 1: Foundation Setup (Must Complete First)
├── Task 1.1: Create Template Directory Structure
├── Task 1.2: Organize Shared Templates ──────────────┐
│   └── (depends on 1.1)                              │
└── Task 1.3: Update config.py with Platform Support  │
    └── (depends on 1.1, 1.2)                         │
                                                      │
PHASE 2: Databricks Template Creation                 │
├── Task 2.1: Create Databricks etl.py Template ─────┘
├── Task 2.2: Create Databricks databricks_utils.py   (parallel with 2.1)
├── Task 2.3: Create Databricks decorators.py         (parallel with 2.1, 2.2)
├── Task 2.4: Create Databricks table_cache.py        (parallel with 2.1-2.3)
├── Task 2.5a: Create Databricks dependencies.py      (parallel with 2.1-2.4)
├── Task 2.5b: Create Databricks credentials.py       (parallel with 2.1-2.5a)
├── Task 2.6: Create Databricks Pipeline Templates    (depends on 2.1-2.5b)
└── Task 2.7: Create Databricks Processor Templates   (depends on 2.1-2.5b)

PHASE 3: Core Manager Refactoring (Depends on Phase 1 & 2)
├── Task 3.1: Update ProjectContext with Platform Property
├── Task 3.2: Update TOMLManager to Store Platform ───┐
│   └── (depends on 3.1)                              │
├── Task 3.3: Update PipelineManager                  │
│   └── (depends on 3.1)                              │
└── Task 3.4: Update ProcessorManager                 │
    └── (depends on 3.1)                              │
                                                      │
PHASE 4: Command Updates (Depends on Phase 3) ────────┘
├── Task 4.1: Update init Command with --platform Flag
│   └── (depends on 3.1, 3.2)
├── Task 4.2: Update create_project() with Platform Support
│   └── (depends on 4.1)
└── Task 4.3: Verify sync-deps Command (No Changes)
    └── (depends on 4.1, 4.2)

PHASE 5: Testing & Validation (Depends on Phase 4)
├── Task 5.1: Create Test Projects for Both Platforms
└── Task 5.2: Test Error Handling Scenarios

PHASE 6: Documentation Updates (Depends on Phase 5)
├── Task 6.1: Update CLAUDE.md
└── Task 6.2: Update README.md
```

## Parallelization Opportunities

- **Phase 2 Tasks 2.1-2.5b**: Can run in parallel (no dependencies between them)
- **Phase 3 Tasks 3.3-3.4**: Can run in parallel after 3.1 is complete
- **Phase 6 Tasks 6.1-6.2**: Can run in parallel

---

## IMPORTANT: CLAUDE.md Update Requirement

**Every task card includes a mandatory requirement to update CLAUDE.md upon completion.** After completing a task, agents MUST:

1. Add a brief entry to CLAUDE.md documenting what was changed
2. Update any affected sections (Architecture, Project Structure, etc.)
3. Include the task ID and a one-line summary

This ensures CLAUDE.md stays synchronized with the codebase as refactoring progresses.

---

# PHASE 1: Foundation Setup

## Task 1.1: Create Template Directory Structure

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the new template directory structure to support multi-platform templates (shared, snowflake, databricks).

**Why it's needed:**
The current template structure has all templates in a flat `templates/init/` directory. To support both Snowflake and Databricks, we need to reorganize templates into platform-specific directories while extracting common files to a shared directory.

**Key implementation details:**

1. Create the new directory structure:
   ```bash
   mkdir -p templates/shared/init
   mkdir -p templates/snowflake/init
   mkdir -p templates/snowflake/pipelines
   mkdir -p templates/snowflake/processors
   mkdir -p templates/databricks/init
   mkdir -p templates/databricks/pipelines
   mkdir -p templates/databricks/processors
   ```

2. The `templates/licenses/` directory remains unchanged at root level.

3. **DO NOT move any files yet** - this task only creates the directory structure.

**Files to be created:**
- `src/pypeline_cli/templates/shared/init/` (empty directory)
- `src/pypeline_cli/templates/snowflake/init/` (empty directory)
- `src/pypeline_cli/templates/snowflake/pipelines/` (empty directory)
- `src/pypeline_cli/templates/snowflake/processors/` (empty directory)
- `src/pypeline_cli/templates/databricks/init/` (empty directory)
- `src/pypeline_cli/templates/databricks/pipelines/` (empty directory)
- `src/pypeline_cli/templates/databricks/processors/` (empty directory)

### Acceptance Criteria

- [ ] Directory `templates/shared/init/` exists
- [ ] Directory `templates/snowflake/init/` exists
- [ ] Directory `templates/snowflake/pipelines/` exists
- [ ] Directory `templates/snowflake/processors/` exists
- [ ] Directory `templates/databricks/init/` exists
- [ ] Directory `templates/databricks/pipelines/` exists
- [ ] Directory `templates/databricks/processors/` exists
- [ ] Existing `templates/licenses/` directory is unchanged
- [ ] Existing `templates/init/`, `templates/pipelines/`, `templates/processors/` directories still exist (not moved yet)
- [ ] Run `pytest` to ensure no tests are broken

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- All existing tests must pass
```

### Dependencies

- **Blocks:** Task 1.2, Task 1.3

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/` (directory structure only)

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under a new "## Refactoring Progress" section (create if not exists):
   ```markdown
   ### Task 1.1: Create Template Directory Structure ✅
   - Created new template directory structure: `templates/shared/`, `templates/snowflake/`, `templates/databricks/`
   - No code changes, directory structure only
   ```

2. Update the "Project Structure" section to show new template directories

---

## Task 1.2: Organize Shared and Snowflake Templates

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Move existing templates to their appropriate locations (shared or Snowflake-specific).

**Why it's needed:**
Templates need to be organized so that platform-agnostic files are in `shared/` and Snowflake-specific files remain accessible for Snowflake projects.

**Key implementation details:**

1. **Copy shared files** (pure Python, no platform dependencies) to `templates/shared/init/`:
   - `databases.py.template`
   - `date_parser.py.template`
   - `logger.py.template`
   - `types.py.template`
   - `basic_test.py.template`
   - `.gitignore.template`
   - `README.md.template`
   - `_init.py.template`

2. **Move platform-specific files** to `templates/snowflake/init/`:
   - `etl.py.template` (uses Snowpark)
   - `snowflake_utils.py.template`
   - `decorators.py.template` (uses Snowflake-specific APIs)
   - `table_cache.py.template` (uses Snowpark DataFrame)
   - `credentials.py.example.template` (Snowflake connection params)

3. **Move dependencies.py.template** from root `templates/` to `templates/snowflake/init/`:
   - Update content to have `BASE_DEPENDENCIES` list with Snowflake packages

4. **Move pipeline templates** to `templates/snowflake/pipelines/`:
   - `runner.py.template`
   - `config.py.template`
   - `README.md.template`
   - `processors_init.py.template`
   - `tests_init.py.template`

5. **Move processor templates** to `templates/snowflake/processors/`:
   - `processor.py.template`
   - `test_processor.py.template`

6. **Delete original files** from `templates/init/`, `templates/pipelines/`, `templates/processors/` after copying (keep original directories empty for now to avoid breaking imports until config.py is updated).

**Files to be modified/created:**
- `templates/shared/init/*.template` (copy from init/)
- `templates/snowflake/init/*.template` (move from init/)
- `templates/snowflake/init/dependencies.py.template` (move from templates/)
- `templates/snowflake/pipelines/*.template` (move from pipelines/)
- `templates/snowflake/processors/*.template` (move from processors/)

### Acceptance Criteria

- [ ] All 8 shared templates exist in `templates/shared/init/`
- [ ] All 5 Snowflake-specific templates exist in `templates/snowflake/init/`
- [ ] `dependencies.py.template` exists in `templates/snowflake/init/` with Snowflake-specific BASE_DEPENDENCIES
- [ ] All 5 pipeline templates exist in `templates/snowflake/pipelines/`
- [ ] Both processor templates exist in `templates/snowflake/processors/`
- [ ] Original files are removed from old locations
- [ ] File contents are unchanged (except dependencies.py.template which gets BASE_DEPENDENCIES)

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- NOTE: Tests may fail after this task until Task 1.3 updates config.py
- Verify files are in correct locations using: find src/pypeline_cli/templates -type f | sort
```

### Dependencies

- **Depends on:** Task 1.1
- **Blocks:** Task 1.3

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- Do not modify config.py - that's Task 1.3
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/shared/init/` (create files)
- `src/pypeline_cli/templates/snowflake/init/` (create files)
- `src/pypeline_cli/templates/snowflake/pipelines/` (create files)
- `src/pypeline_cli/templates/snowflake/processors/` (create files)
- `src/pypeline_cli/templates/init/` (remove files)
- `src/pypeline_cli/templates/pipelines/` (remove files)
- `src/pypeline_cli/templates/processors/` (remove files)
- `src/pypeline_cli/templates/dependencies.py.template` (move)

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 1.2: Organize Shared and Snowflake Templates ✅
   - Moved shared templates to `templates/shared/init/`
   - Moved Snowflake-specific templates to `templates/snowflake/`
   - Updated dependencies.py.template with BASE_DEPENDENCIES structure
   ```

2. Update the "Template System" section to reflect new organization

---

## Task 1.3: Update config.py with Platform Support

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update `src/pypeline_cli/config.py` to support multi-platform template paths and add platform detection functionality.

**Why it's needed:**
The config.py currently has hardcoded paths to templates. It needs to be updated to dynamically select templates based on the target platform (Snowflake or Databricks).

**Key implementation details:**

1. **Add Platform enum**:
   ```python
   from enum import Enum

   class Platform(str, Enum):
       """Supported platforms for pypeline projects."""
       SNOWFLAKE = "snowflake"
       DATABRICKS = "databricks"
   ```

2. **Add helper function to read platform from pyproject.toml**:
   ```python
   def get_platform_from_toml(toml_path: Path | None = None) -> str | None:
       """Read platform from pyproject.toml [tool.pypeline] section."""
       # Implementation as specified in REFACTOR_PLAN.md
   ```

3. **Update template path constants**:
   ```python
   PATH_TO_TEMPLATES = Path(__file__).parent / "templates"
   PATH_TO_SHARED_INIT = PATH_TO_TEMPLATES / "shared" / "init"
   PATH_TO_LICENSES = PATH_TO_TEMPLATES / "licenses"

   def get_platform_init_path(platform: str) -> Path:
       return PATH_TO_TEMPLATES / platform / "init"

   def get_platform_pipelines_path(platform: str) -> Path:
       return PATH_TO_TEMPLATES / platform / "pipelines"

   def get_platform_processors_path(platform: str) -> Path:
       return PATH_TO_TEMPLATES / platform / "processors"
   ```

4. **Add shared scaffold files list**:
   ```python
   SHARED_SCAFFOLD_FILES = [
       ScaffoldFile(
           template_name=PATH_TO_SHARED_INIT / "databases.py.template",
           destination_property="databases_file",
       ),
       # ... other shared files
   ]
   ```

5. **Add function to get platform-specific scaffold files**:
   ```python
   def get_platform_scaffold_files(platform: str) -> list[ScaffoldFile]:
       """Get platform-specific scaffold files dynamically."""
       # Implementation as specified in REFACTOR_PLAN.md
   ```

6. **Keep existing INIT_SCAFFOLD_FILES for backwards compatibility** but deprecate it (or update to use Snowflake as default).

7. **Remove or update DEFAULT_DEPENDENCIES** since dependencies are now platform-specific.

**Files to be modified:**
- `src/pypeline_cli/config.py`

### Acceptance Criteria

- [ ] Platform enum is defined with SNOWFLAKE and DATABRICKS values
- [ ] `get_platform_from_toml()` function works correctly
- [ ] Path helper functions return correct paths for both platforms
- [ ] `SHARED_SCAFFOLD_FILES` list contains 8 shared template references
- [ ] `get_platform_scaffold_files()` returns combined shared + platform files
- [ ] Import config.py without errors
- [ ] All paths point to valid template files
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Run: python -c "from pypeline_cli.config import Platform, get_platform_scaffold_files; print(get_platform_scaffold_files('snowflake'))"
- All tests must pass
```

### Dependencies

- **Depends on:** Task 1.1, Task 1.2
- **Blocks:** Phase 2, Phase 3

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/config.py`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 1.3: Update config.py with Platform Support ✅
   - Added Platform enum (SNOWFLAKE, DATABRICKS)
   - Added get_platform_from_toml() helper function
   - Added platform-aware path helpers and scaffold file functions
   ```

2. Update the "Architecture" section to document:
   - Platform enum and its values
   - `get_platform_from_toml()` function
   - `get_platform_scaffold_files()` function
   - Path helper functions

---

# PHASE 2: Databricks Template Creation

## Task 2.1: Create Databricks etl.py Template

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the Databricks-specific ETL singleton template at `templates/databricks/init/etl.py.template`.

**Why it's needed:**
Databricks uses DatabricksSession (from databricks-connect) instead of Snowpark Session. The ETL singleton needs to be adapted for Databricks workspace authentication with credentials file fallback.

**Key implementation details:**

Reference the implementation in REFACTOR_PLAN.md Task 2.1. The template should:

1. Import `DatabricksSession` from `databricks.connect`
2. Try credentials file import with fallback handling
3. Implement singleton pattern
4. Use dual connection strategy:
   - Try `DatabricksSession.builder.getOrCreate()` first (workspace)
   - Fall back to credentials.py if available
5. Include proper docstrings and type hints
6. Mark as "Framework File - Do Not Modify"

**Files to be created:**
- `src/pypeline_cli/templates/databricks/init/etl.py.template`

### Acceptance Criteria

- [ ] Template file exists at `templates/databricks/init/etl.py.template`
- [ ] Uses `DatabricksSession` from `databricks.connect`
- [ ] Implements singleton pattern matching Snowflake version structure
- [ ] Has dual connection strategy (workspace first, credentials fallback)
- [ ] Includes proper docstrings and usage examples
- [ ] Has "Framework File - Do Not Modify" header
- [ ] Template is valid Python syntax (can be imported after variable substitution)

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Verify syntax: python -m py_compile <path_to_template_renamed_to_.py>
- Compare structure with templates/snowflake/init/etl.py.template
```

### Dependencies

- **Depends on:** Task 1.3
- **Parallel with:** Tasks 2.2, 2.3, 2.4, 2.5a, 2.5b

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- Follow the exact structure from REFACTOR_PLAN.md
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/init/etl.py.template`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.1: Create Databricks etl.py Template ✅
   - Created `templates/databricks/init/etl.py.template`
   - Uses DatabricksSession with workspace + credentials fallback
   ```

---

## Task 2.2: Create Databricks databricks_utils.py Template

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the Databricks-specific utilities template at `templates/databricks/init/databricks_utils.py.template`.

**Why it's needed:**
Databricks uses Unity Catalog instead of Snowflake's catalog system. The utility functions need to query `system.information_schema.tables` and use PySpark APIs instead of Snowpark.

**Key implementation details:**

Reference the implementation in REFACTOR_PLAN.md Task 2.2. The template should include:

1. **Imports:**
   - `from pyspark.sql import SparkSession`
   - `from .types import TableConfig, TimestampResult, ParsedTablePath`

2. **Functions:**
   - `get_table_last_modified()` - Query Unity Catalog INFORMATION_SCHEMA
   - `check_table_exists()` - Use `session.catalog.tableExists()`
   - `check_table_read_access()` - Attempt minimal SELECT query
   - `parse_table_path()` - Convert TableConfig to ParsedTablePath

3. **Key differences from snowflake_utils.py:**
   - Uses `system.information_schema.tables` (Unity Catalog)
   - Uses `session.catalog.tableExists()` directly
   - Parameters use `catalog_name` instead of `database_name`

**Files to be created:**
- `src/pypeline_cli/templates/databricks/init/databricks_utils.py.template`

### Acceptance Criteria

- [ ] Template file exists at `templates/databricks/init/databricks_utils.py.template`
- [ ] Uses PySpark imports (`from pyspark.sql import SparkSession`)
- [ ] All 4 functions implemented with matching signatures to snowflake_utils
- [ ] Uses Unity Catalog APIs (system.information_schema, session.catalog.tableExists)
- [ ] Includes proper docstrings and type hints
- [ ] Has "Framework File - Do Not Modify" header

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify syntax: python -m py_compile <path_to_template_renamed_to_.py>
- Compare with templates/snowflake/init/snowflake_utils.py.template for parity
```

### Dependencies

- **Depends on:** Task 1.3
- **Parallel with:** Tasks 2.1, 2.3, 2.4, 2.5a, 2.5b

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- Follow the exact structure from REFACTOR_PLAN.md
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/init/databricks_utils.py.template`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.2: Create Databricks databricks_utils.py Template ✅
   - Created `templates/databricks/init/databricks_utils.py.template`
   - Uses Unity Catalog APIs for table operations
   ```

---

## Task 2.3: Create Databricks decorators.py Template

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the Databricks-specific decorators template at `templates/databricks/init/decorators.py.template`.

**Why it's needed:**
The decorators that check table existence and freshness need to use Databricks/PySpark APIs instead of Snowflake-specific functions.

**Key implementation details:**

1. **`@time_function()`** - Unchanged (pure Python, no platform dependencies)

2. **`@skip_if_exists()`** - Modify to use:
   - `session.catalog.tableExists()` instead of Snowflake's catalog API

3. **`@skip_if_updated_this_month()`** - Modify to:
   - Query `system.information_schema.tables` for `last_altered` timestamp
   - Instead of using `SYSTEM$LAST_CHANGE_COMMIT_TIME()`

4. Read the existing Snowflake `decorators.py.template` as reference and adapt for Databricks.

**Files to be created:**
- `src/pypeline_cli/templates/databricks/init/decorators.py.template`

### Acceptance Criteria

- [ ] Template file exists at `templates/databricks/init/decorators.py.template`
- [ ] `@time_function` decorator is included (unchanged from Snowflake)
- [ ] `@skip_if_exists` uses `session.catalog.tableExists()`
- [ ] `@skip_if_updated_this_month` queries Unity Catalog information_schema
- [ ] All decorators have proper docstrings
- [ ] Has "Framework File - Do Not Modify" header

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify syntax: python -m py_compile <path_to_template_renamed_to_.py>
- Compare with templates/snowflake/init/decorators.py.template
```

### Dependencies

- **Depends on:** Task 1.3
- **Parallel with:** Tasks 2.1, 2.2, 2.4, 2.5a, 2.5b

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- First read the Snowflake decorators.py.template for reference
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/init/decorators.py.template`
- `src/pypeline_cli/templates/snowflake/init/decorators.py.template` (reference)

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.3: Create Databricks decorators.py Template ✅
   - Created `templates/databricks/init/decorators.py.template`
   - Adapted @skip_if_exists and @skip_if_updated_this_month for Unity Catalog
   ```

---

## Task 2.4: Create Databricks table_cache.py Template

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the Databricks-specific table cache template at `templates/databricks/init/table_cache.py.template`.

**Why it's needed:**
The TableCache needs to use PySpark DataFrame instead of Snowpark DataFrame for type hints and table loading.

**Key implementation details:**

1. **Import changes:**
   - Change: `from snowflake.snowpark import DataFrame`
   - To: `from pyspark.sql import DataFrame`

2. **Table loading:**
   - `self.etl.session.table(table_name)` works the same (Unity Catalog aware)
   - No changes needed to the table loading logic

3. Near-identical structure to Snowflake version with only import changes.

**Files to be created:**
- `src/pypeline_cli/templates/databricks/init/table_cache.py.template`

### Acceptance Criteria

- [ ] Template file exists at `templates/databricks/init/table_cache.py.template`
- [ ] Uses `from pyspark.sql import DataFrame`
- [ ] TableCache class structure matches Snowflake version
- [ ] Methods: `add_table()`, `get_table()`, `preload_tables()`, `tables` property
- [ ] Includes proper docstrings
- [ ] Has "Framework File - Do Not Modify" header

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify syntax: python -m py_compile <path_to_template_renamed_to_.py>
- Diff with templates/snowflake/init/table_cache.py.template to verify only import changes
```

### Dependencies

- **Depends on:** Task 1.3
- **Parallel with:** Tasks 2.1, 2.2, 2.3, 2.5a, 2.5b

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- First read the Snowflake table_cache.py.template for reference
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/init/table_cache.py.template`
- `src/pypeline_cli/templates/snowflake/init/table_cache.py.template` (reference)

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.4: Create Databricks table_cache.py Template ✅
   - Created `templates/databricks/init/table_cache.py.template`
   - Uses PySpark DataFrame imports
   ```

---

## Task 2.5a: Create Databricks dependencies.py Template

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the Databricks-specific dependencies template at `templates/databricks/init/dependencies.py.template`.

**Why it's needed:**
Databricks projects need different dependencies than Snowflake (PySpark, Delta Lake instead of Snowpark).

**Key implementation details:**

1. Create file with `BASE_DEPENDENCIES` containing Databricks-specific packages:
   ```python
   BASE_DEPENDENCIES = [
       "pyspark>=3.5.0",
       "delta-spark>=3.0.0",
       "databricks-connect>=13.0.0",
       "numpy>=2.2.6",
       "pandas>=2.3.3",
       "build==1.3.0",
       "twine==6.2.0",
       "ruff==0.14.9",
       "pre-commit==4.5.1",
       "pytest==9.0.2",
       "pytest-cov==7.0.0",
   ]
   ```

2. Include `USER_DEPENDENCIES` section (empty list for user additions)

3. Include `DEFAULT_DEPENDENCIES = BASE_DEPENDENCIES + USER_DEPENDENCIES`

4. Follow same structure as Snowflake dependencies.py.template

**Files to be created:**
- `src/pypeline_cli/templates/databricks/init/dependencies.py.template`

### Acceptance Criteria

- [ ] Template file exists at `templates/databricks/init/dependencies.py.template`
- [ ] Contains `BASE_DEPENDENCIES` with Databricks packages (pyspark, delta-spark, databricks-connect)
- [ ] Contains empty `USER_DEPENDENCIES` list
- [ ] Contains `DEFAULT_DEPENDENCIES = BASE_DEPENDENCIES + USER_DEPENDENCIES`
- [ ] Includes docstring explaining usage

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify syntax: python -m py_compile <path_to_template_renamed_to_.py>
- Compare structure with templates/snowflake/init/dependencies.py.template
```

### Dependencies

- **Depends on:** Task 1.3
- **Parallel with:** Tasks 2.1, 2.2, 2.3, 2.4, 2.5b

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/init/dependencies.py.template`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.5a: Create Databricks dependencies.py Template ✅
   - Created `templates/databricks/init/dependencies.py.template`
   - Includes pyspark, delta-spark, databricks-connect dependencies
   ```

---

## Task 2.5b: Create Databricks credentials.py.example Template

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create the Databricks-specific credentials example template at `templates/databricks/init/credentials.py.example.template`.

**Why it's needed:**
Databricks uses different authentication parameters than Snowflake (host, token, cluster ID).

**Key implementation details:**

Create file with Databricks authentication parameters:
```python
"""
Databricks credentials for local development.

Copy this file to 'credentials.py' and fill in your values.
This file is used when running outside of Databricks workspace.

⚠️ NEVER commit credentials.py to version control!
"""

# Databricks workspace URL (e.g., https://adb-xxx.azuredatabricks.net)
DATABRICKS_HOST = "https://your-workspace.azuredatabricks.net"

# Personal Access Token (PAT)
DATABRICKS_TOKEN = "your-personal-access-token"

# Cluster ID for compute
DATABRICKS_CLUSTER_ID = "your-cluster-id"
```

**Files to be created:**
- `src/pypeline_cli/templates/databricks/init/credentials.py.example.template`

### Acceptance Criteria

- [ ] Template file exists at `templates/databricks/init/credentials.py.example.template`
- [ ] Contains `DATABRICKS_HOST` variable with example value
- [ ] Contains `DATABRICKS_TOKEN` variable with placeholder
- [ ] Contains `DATABRICKS_CLUSTER_ID` variable with placeholder
- [ ] Includes warning about not committing credentials
- [ ] Includes docstring explaining purpose and usage

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify file exists and has correct content
- Compare with templates/snowflake/init/credentials.py.example.template for structure
```

### Dependencies

- **Depends on:** Task 1.3
- **Parallel with:** Tasks 2.1, 2.2, 2.3, 2.4, 2.5a

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/init/credentials.py.example.template`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.5b: Create Databricks credentials.py.example Template ✅
   - Created `templates/databricks/init/credentials.py.example.template`
   - Includes DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_CLUSTER_ID
   ```

---

## Task 2.6: Create Databricks Pipeline Templates

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create all Databricks-specific pipeline templates in `templates/databricks/pipelines/`.

**Why it's needed:**
Pipeline templates need to use PySpark APIs and Delta Lake write operations instead of Snowpark.

**Key implementation details:**

1. **runner.py.template:**
   - Import: `from pyspark.sql import DataFrame`
   - Rename write method: `_write_to_databricks()` instead of `_write_to_snowflake()`
   - Write operation: `df.write.format("delta").mode(write_mode).saveAsTable(table_path)`

2. **config.py.template:**
   - Same as Snowflake (uses TableConfig which is platform-agnostic)

3. **README.md.template:**
   - Update references to "Databricks" and "Unity Catalog"
   - Change example commands/imports accordingly

4. **processors_init.py.template:**
   - Same as Snowflake (just package marker)

5. **tests_init.py.template:**
   - Same as Snowflake (just package marker)

**Files to be created:**
- `src/pypeline_cli/templates/databricks/pipelines/runner.py.template`
- `src/pypeline_cli/templates/databricks/pipelines/config.py.template`
- `src/pypeline_cli/templates/databricks/pipelines/README.md.template`
- `src/pypeline_cli/templates/databricks/pipelines/processors_init.py.template`
- `src/pypeline_cli/templates/databricks/pipelines/tests_init.py.template`

### Acceptance Criteria

- [ ] All 5 template files exist in `templates/databricks/pipelines/`
- [ ] runner.py.template uses `from pyspark.sql import DataFrame`
- [ ] runner.py.template has `_write_to_databricks()` method
- [ ] Write operation uses Delta format: `df.write.format("delta").mode().saveAsTable()`
- [ ] README.md.template references Databricks and Unity Catalog
- [ ] All templates have correct variable placeholders ($class_name, $pipeline_name, $project_name)

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify syntax of Python templates: python -m py_compile <path>
- Compare with templates/snowflake/pipelines/ for structural parity
```

### Dependencies

- **Depends on:** Tasks 2.1-2.5b (all init templates)
- **Blocks:** Task 2.7

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- First read the Snowflake pipeline templates for reference
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/pipelines/runner.py.template`
- `src/pypeline_cli/templates/databricks/pipelines/config.py.template`
- `src/pypeline_cli/templates/databricks/pipelines/README.md.template`
- `src/pypeline_cli/templates/databricks/pipelines/processors_init.py.template`
- `src/pypeline_cli/templates/databricks/pipelines/tests_init.py.template`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.6: Create Databricks Pipeline Templates ✅
   - Created all 5 Databricks pipeline templates
   - runner.py uses PySpark DataFrame and Delta Lake writes
   ```

---

## Task 2.7: Create Databricks Processor Templates

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create all Databricks-specific processor templates in `templates/databricks/processors/`.

**Why it's needed:**
Processor templates need to use PySpark DataFrame and functions instead of Snowpark equivalents.

**Key implementation details:**

1. **processor.py.template:**
   - Import: `from pyspark.sql import DataFrame`
   - Import: `from pyspark.sql.functions import col` (instead of snowflake.snowpark.functions)
   - Rest of logic remains identical (APIs are compatible)

2. **test_processor.py.template:**
   - Same as Snowflake version (pytest patterns are platform-agnostic)
   - Mock imports updated to PySpark if needed

**Files to be created:**
- `src/pypeline_cli/templates/databricks/processors/processor.py.template`
- `src/pypeline_cli/templates/databricks/processors/test_processor.py.template`

### Acceptance Criteria

- [ ] Both template files exist in `templates/databricks/processors/`
- [ ] processor.py.template uses `from pyspark.sql import DataFrame`
- [ ] processor.py.template uses `from pyspark.sql.functions import col`
- [ ] processor.py.template has same structure as Snowflake version
- [ ] test_processor.py.template has pytest fixtures for PySpark mocks
- [ ] All templates have correct variable placeholders

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Verify syntax of Python templates: python -m py_compile <path>
- Compare with templates/snowflake/processors/ for structural parity
```

### Dependencies

- **Depends on:** Tasks 2.1-2.5b (all init templates)
- **Blocks:** Phase 3

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- First read the Snowflake processor templates for reference
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/templates/databricks/processors/processor.py.template`
- `src/pypeline_cli/templates/databricks/processors/test_processor.py.template`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 2.7: Create Databricks Processor Templates ✅
   - Created both Databricks processor templates
   - Uses PySpark DataFrame and functions imports
   ```

2. Update the "Template System" section to note that Phase 2 (Databricks templates) is complete

---

# PHASE 3: Core Manager Refactoring

## Task 3.1: Update ProjectContext with Platform Property

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update `ProjectContext` class to add platform detection and platform-specific path properties.

**Why it's needed:**
ProjectContext needs to know which platform a project is configured for so that managers can select appropriate templates.

**Key implementation details:**

1. **Add platform property:**
   ```python
   @property
   def platform(self) -> str:
       """Get platform from pyproject.toml."""
       # Read [tool.pypeline].platform from toml_path
       # Raise ValueError if platform not set
   ```

2. **Add platform_utils_file property:**
   ```python
   @property
   def platform_utils_file(self) -> Path:
       """Get platform-specific utils file path."""
       platform = self.platform
       return self.project_utils_folder_path / f"{platform}_utils.py"
   ```

3. **Remove or deprecate snowflake_utils_file property** (breaking change acceptable).

4. Reference the implementation in REFACTOR_PLAN.md Task 3.1.

**Files to be modified:**
- `src/pypeline_cli/core/managers/project_context.py`

### Acceptance Criteria

- [ ] `platform` property reads from pyproject.toml `[tool.pypeline].platform`
- [ ] `platform` property raises ValueError with clear message if platform not set
- [ ] `platform_utils_file` property returns correct path for both platforms
- [ ] Old `snowflake_utils_file` property is removed or deprecated
- [ ] All existing tests pass
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Manual test: Create test toml with platform, verify property returns correct value
```

### Dependencies

- **Depends on:** Phase 1, Phase 2
- **Blocks:** Tasks 3.2, 3.3, 3.4, Phase 4

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/core/managers/project_context.py`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 3.1: Update ProjectContext with Platform Property ✅
   - Added `platform` property that reads from pyproject.toml
   - Added `platform_utils_file` property for dynamic path resolution
   - Removed deprecated `snowflake_utils_file` property
   ```

2. Update the "Manager Pattern" section for ProjectContext to document new properties

---

## Task 3.2: Update TOMLManager to Store Platform

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update `TOMLManager` class to accept and store platform in pyproject.toml.

**Why it's needed:**
When creating a new project, the platform selection needs to be persisted in pyproject.toml so other commands can read it.

**Key implementation details:**

1. **Add platform parameter to create():**
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

2. **Store platform in [tool.pypeline]:**
   ```python
   "tool": {
       "pypeline": {
           "managed": True,
           "platform": platform,  # NEW FIELD
       },
   }
   ```

3. **Remove platform-specific dependencies from pyproject.toml:**
   - Dependencies are now defined in platform-specific `dependencies.py.template`
   - Initial `pyproject.toml` should have minimal/empty dependencies list

**Files to be modified:**
- `src/pypeline_cli/core/managers/toml_manager.py`

### Acceptance Criteria

- [ ] `create()` method accepts `platform` parameter
- [ ] Generated pyproject.toml has `[tool.pypeline].platform` field
- [ ] Platform value is correctly stored (e.g., "snowflake" or "databricks")
- [ ] Dependencies list is empty or minimal (not platform-specific)
- [ ] All existing tests pass after update
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Manual test: Create test project, verify pyproject.toml has platform field
```

### Dependencies

- **Depends on:** Task 3.1
- **Blocks:** Task 4.1, Task 4.2

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/core/managers/toml_manager.py`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 3.2: Update TOMLManager to Store Platform ✅
   - Added `platform` parameter to `create()` method
   - Platform stored in `[tool.pypeline].platform` field
   ```

2. Update the "Manager Pattern" section for TOMLManager

---

## Task 3.3: Update PipelineManager with Platform Awareness

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update `PipelineManager` class to read platform from context and use platform-specific template paths.

**Why it's needed:**
When creating pipelines, the manager needs to use Snowflake or Databricks templates based on the project's configured platform.

**Key implementation details:**

1. **Read platform from context in __init__():**
   ```python
   def __init__(self, ctx: ProjectContext) -> None:
       self.ctx = ctx
       self.platform = ctx.platform

       from ...config import get_platform_pipelines_path
       self.templates_path = get_platform_pipelines_path(self.platform)
   ```

2. **Update any hardcoded template paths** to use `self.templates_path`.

3. No other changes needed - template substitution logic is platform-agnostic.

**Files to be modified:**
- `src/pypeline_cli/core/managers/pipeline_manager.py`

### Acceptance Criteria

- [ ] `__init__()` reads platform from `ctx.platform`
- [ ] `templates_path` is set dynamically based on platform
- [ ] Correct templates are used for each platform
- [ ] All existing tests pass
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Verify correct template directory is selected based on platform
```

### Dependencies

- **Depends on:** Task 3.1
- **Parallel with:** Task 3.4

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/core/managers/pipeline_manager.py`

### Post-Completion: Update CLAUDE.md

After completing this task, you MUST update CLAUDE.md:

1. Add entry under "## Refactoring Progress" section:
   ```markdown
   ### Task 3.3: Update PipelineManager with Platform Awareness ✅
   - Reads platform from `ctx.platform`
   - Uses dynamic template paths via `get_platform_pipelines_path()`
   ```

---

## Task 3.4: Update ProcessorManager with Platform Awareness

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update `ProcessorManager` class to read platform from context and use platform-specific template paths.

**Why it's needed:**
When creating processors, the manager needs to use Snowflake or Databricks templates based on the project's configured platform.

**Key implementation details:**

1. **Read platform from context in __init__():**
   ```python
   def __init__(self, ctx: ProjectContext) -> None:
       self.ctx = ctx
       self.platform = ctx.platform

       from ...config import get_platform_processors_path
       self.templates_path = get_platform_processors_path(self.platform)
   ```

2. **Update any hardcoded template paths** to use `self.templates_path`.

3. No other changes needed.

**Files to be modified:**
- `src/pypeline_cli/core/managers/processor_manager.py`

### Acceptance Criteria

- [ ] `__init__()` reads platform from `ctx.platform`
- [ ] `templates_path` is set dynamically based on platform
- [ ] Correct templates are used for each platform
- [ ] All existing tests pass
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Verify correct template directory is selected based on platform
```

### Dependencies

- **Depends on:** Task 3.1
- **Parallel with:** Task 3.3

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/core/managers/processor_manager.py`

---

# PHASE 4: Command Updates

## Task 4.1: Update init Command with --platform Flag

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update the `init` command to accept a `--platform` flag for selecting target platform.

**Why it's needed:**
Users need to specify which platform (Snowflake or Databricks) they want to target when creating a new project.

**Key implementation details:**

1. **Add --platform option:**
   ```python
   @click.option(
       "--platform",
       type=click.Choice(["snowflake", "databricks"], case_sensitive=False),
       prompt="Select target platform",
       default="snowflake",
       help="Target platform for the pipeline (snowflake or databricks)",
       show_choices=True,
   )
   ```

2. **Add platform parameter to function signature:**
   ```python
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

3. **Pass platform to create_project():**
   ```python
   create_project(
       ctx=ctx,
       name=name,
       ...
       platform=platform,
   )
   ```

4. **Update success message:**
   ```python
   click.echo(f"\n✅ Successfully created {platform} project '{name}'!")
   ```

**Files to be modified:**
- `src/pypeline_cli/commands/init.py`

### Acceptance Criteria

- [ ] `--platform` option appears in `pypeline init --help`
- [ ] Platform defaults to "snowflake" if not specified
- [ ] Platform is validated to be "snowflake" or "databricks"
- [ ] Platform is passed to create_project()
- [ ] Success message includes platform name
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pypeline init --help (verify --platform option)
- Run: pytest --no-cov
```

### Dependencies

- **Depends on:** Tasks 3.1, 3.2
- **Blocks:** Task 4.2

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/commands/init.py`

---

## Task 4.2: Update create_project() with Platform Support

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update the `create_project()` function to accept platform parameter and use platform-specific scaffold files.

**Why it's needed:**
The project creation orchestration needs to select and use the correct templates based on the target platform.

**Key implementation details:**

1. **Add platform parameter:**
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

2. **Pass platform to TOMLManager.create():**
   ```python
   toml_manager.create(
       name=name,
       ...
       platform=platform,
       use_git=use_git,
   )
   ```

3. **Use platform-specific scaffold files:**
   ```python
   from ..config import get_platform_scaffold_files

   scaffold_files = get_platform_scaffold_files(platform)
   scaffolding_manager.create_files_from_templates(scaffold_files=scaffold_files)
   ```

**Files to be modified:**
- `src/pypeline_cli/core/create_project.py`

### Acceptance Criteria

- [ ] `create_project()` accepts `platform` parameter
- [ ] Platform is passed to TOMLManager.create()
- [ ] Platform-specific scaffold files are used
- [ ] Correct templates are copied for each platform
- [ ] All existing tests pass
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Run: scripts/create_test_project.py (may need modification for platform flag)
```

### Dependencies

- **Depends on:** Task 4.1
- **Blocks:** Task 4.3

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- You MUST test your implementation using pytest before completion
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/core/create_project.py`

---

## Task 4.3: Verify sync-deps Command Compatibility

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Verify that the `sync-deps` command works correctly with the new platform-specific dependencies structure.

**Why it's needed:**
The sync-deps command reads from dependencies.py and writes to pyproject.toml. We need to ensure it still works now that dependencies are platform-specific.

**Key implementation details:**

1. **Review current sync-deps implementation:**
   - Read `src/pypeline_cli/commands/sync_deps.py`
   - Understand how it reads from dependencies.py
   - Understand how it writes to pyproject.toml

2. **Verify compatibility:**
   - The command reads `DEFAULT_DEPENDENCIES` from user's dependencies.py
   - Dependencies.py is now platform-specific (has BASE_DEPENDENCIES)
   - Command should work unchanged since it just reads DEFAULT_DEPENDENCIES

3. **Test error handling:**
   - If platform is missing from pyproject.toml, `ProjectContext.platform` should raise clear error
   - Verify this error is propagated correctly

4. **No changes should be needed** - this is a verification task.

**Files to be reviewed (not modified unless necessary):**
- `src/pypeline_cli/commands/sync_deps.py`

### Acceptance Criteria

- [ ] sync-deps command works with new project structure
- [ ] Dependencies from dependencies.py are synced to pyproject.toml
- [ ] Clear error message if platform missing from pyproject.toml
- [ ] All existing tests pass
- [ ] Run `pytest` - all tests should pass

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: pytest --no-cov
- Create test project, modify dependencies.py, run pypeline sync-deps
- Verify pyproject.toml is updated correctly
```

### Dependencies

- **Depends on:** Tasks 4.1, 4.2

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before making any changes
- This is primarily a VERIFICATION task - minimize code changes
- Document any issues found
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/commands/sync_deps.py` (review only)

---

# PHASE 5: Testing & Validation

## Task 5.1: Create Test Projects for Both Platforms

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Create end-to-end test projects for both Snowflake and Databricks platforms to verify the refactoring works correctly.

**Why it's needed:**
We need to validate that the entire workflow (init, create-pipeline, create-processor) works for both platforms.

**Key implementation details:**

1. **Update scripts/create_test_project.py** to support platform parameter:
   - Add `--platform` argument (default: snowflake)
   - Pass platform to `pypeline init`

2. **Create Snowflake test project:**
   ```bash
   pypeline init \
     --destination ./test-snowflake \
     --name test_snowflake \
     --platform snowflake \
     --no-git
   ```

3. **Create Databricks test project:**
   ```bash
   pypeline init \
     --destination ./test-databricks \
     --name test_databricks \
     --platform databricks \
     --no-git
   ```

4. **Verify file structure for each:**
   - Snowflake: `utils/snowflake_utils.py` exists
   - Databricks: `utils/databricks_utils.py` exists
   - Both: Correct imports in etl.py, runner templates

5. **Create pipeline in each:**
   ```bash
   cd test-snowflake && pypeline create-pipeline --name test-pipeline
   cd test-databricks && pypeline create-pipeline --name test-pipeline
   ```

6. **Create processor in each:**
   ```bash
   pypeline create-processor --name test-processor --pipeline test-pipeline
   ```

7. **Verify templates:**
   - Snowflake: Uses `snowflake.snowpark` imports
   - Databricks: Uses `pyspark.sql` imports

**Files to be modified:**
- `scripts/create_test_project.py`

### Acceptance Criteria

- [ ] scripts/create_test_project.py supports `--platform` argument
- [ ] Snowflake test project creates successfully
- [ ] Databricks test project creates successfully
- [ ] Snowflake project has snowflake_utils.py
- [ ] Databricks project has databricks_utils.py
- [ ] Pipeline creation works for both platforms
- [ ] Processor creation works for both platforms
- [ ] Correct imports in generated files for each platform

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Test scripts location: scripts/
- Run: python scripts/create_test_project.py --platform snowflake
- Run: python scripts/create_test_project.py --platform databricks
- Inspect generated files for correctness
```

### Dependencies

- **Depends on:** Phase 4 (all command updates complete)
- **Blocks:** Task 5.2

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing any code
- You can modify code ONLY after plan approval
- Clean up test projects after verification
- Use the existing .venv or tests may fail
```

### Critical Files

- `scripts/create_test_project.py`
- Generated test projects (temporary)

---

## Task 5.2: Test Error Handling Scenarios

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Test error handling for edge cases and invalid configurations.

**Why it's needed:**
We need to ensure clear, helpful error messages when users encounter issues.

**Key implementation details:**

1. **Test missing platform field:**
   - Manually remove platform field from pyproject.toml
   - Run `pypeline create-pipeline` or `pypeline sync-deps`
   - Verify clear error message:
     ```
     Platform not set in pyproject.toml.
     Add 'platform = "snowflake"' or 'platform = "databricks"'
     to [tool.pypeline] section.
     ```

2. **Test invalid platform value:**
   - Set `platform = "invalid"` in pyproject.toml
   - Run any pypeline command
   - Verify appropriate error message

3. **Test platform detection outside project:**
   - Run `pypeline create-pipeline` outside a pypeline project
   - Verify error about not finding pypeline project

4. **Document all error scenarios tested and their messages.**

**Files to be reviewed:**
- Various command files to verify error handling

### Acceptance Criteria

- [ ] Missing platform field produces clear error message
- [ ] Invalid platform value produces clear error message
- [ ] Running commands outside project produces clear error
- [ ] All error messages include actionable guidance
- [ ] No stack traces shown to users (clean error handling)

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Create test project, then modify pyproject.toml to test scenarios
- Document each error scenario and the message produced
```

### Dependencies

- **Depends on:** Task 5.1

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before any modifications
- This is primarily a TESTING task - document findings
- Fix any missing error handling discovered
- Use the existing .venv or tests may fail
```

### Critical Files

- `src/pypeline_cli/core/managers/project_context.py` (error handling)
- `src/pypeline_cli/commands/*.py` (error handling)

---

# PHASE 6: Documentation Updates

## Task 6.1: Update CLAUDE.md

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update CLAUDE.md to document the new multi-platform support architecture.

**Why it's needed:**
CLAUDE.md serves as the primary reference for Claude Code agents working on this codebase. It needs to reflect the new platform-aware architecture.

**Key implementation details:**

1. **Add Platform Support section:**
   ```markdown
   ## Platform Support

   pypeline-cli supports two platforms:
   - **Snowflake**: Uses Snowpark for DataFrame operations
   - **Databricks**: Uses PySpark with Unity Catalog and Delta tables

   Platform is selected during `pypeline init` via the `--platform` flag.
   ```

2. **Add Platform-Specific Templates section:**
   ```markdown
   ### Template Organization

   Templates are organized by platform:
   - `templates/shared/` - Pure Python files (no platform dependencies)
   - `templates/snowflake/` - Snowpark-specific implementations
   - `templates/databricks/` - PySpark-specific implementations
   - `templates/licenses/` - License templates (shared)
   ```

3. **Add Platform Selection section:**
   - Document `--platform` flag usage
   - Document storage in `pyproject.toml [tool.pypeline]`

4. **Update Architecture section:**
   - Document new config.py structure
   - Document Platform enum and helper functions
   - Document how managers read platform

5. **Update Project Structure section:**
   - Show new template directory structure

**Files to be modified:**
- `CLAUDE.md`

### Acceptance Criteria

- [ ] Platform Support section added
- [ ] Template Organization documented
- [ ] Platform Selection documented
- [ ] Architecture section updated with config.py changes
- [ ] Project Structure shows new template layout
- [ ] All examples updated to include --platform flag
- [ ] Document is consistent and well-formatted

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Review CLAUDE.md for completeness and accuracy
- Verify all referenced paths and commands are correct
```

### Dependencies

- **Depends on:** Phase 5 (all testing complete)
- **Parallel with:** Task 6.2

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing
- Keep documentation concise but complete
- Ensure all examples are accurate
```

### Critical Files

- `CLAUDE.md`

---

## Task 6.2: Update README.md

### Introduction

You are a worker agent tasked to refactor a part of this codebase. CLAUDE.md contains a quick reference to the project. You are responsible for the following task:

### Task Description

**What needs to be done:**
Update README.md to document multi-platform support for end users.

**Why it's needed:**
The README is the first thing users see. It needs to clearly explain how to create projects for different platforms.

**Key implementation details:**

1. **Update Quick Start section:**
   ```markdown
   ## Getting Started

   Create a new pipeline project:

   ```bash
   # Snowflake project (default)
   pypeline init --platform snowflake --name my-snowflake-pipeline

   # Databricks project
   pypeline init --platform databricks --name my-databricks-pipeline
   ```

2. **Update Command Reference for `pypeline init`:**
   - Document `--platform` option
   - Show default value (snowflake)
   - List valid choices

3. **Add Platform-Specific Sections:**
   - Document Snowflake-specific features
   - Document Databricks-specific features
   - Note API differences (DataFrame imports, write methods)

4. **Update any examples** that assume Snowflake-only

5. **Update Requirements section** if Databricks has different requirements

**Files to be modified:**
- `README.md`

### Acceptance Criteria

- [ ] Quick Start shows both platform options
- [ ] `pypeline init` command reference includes --platform
- [ ] Platform-specific features documented
- [ ] All examples updated or clarified for platform context
- [ ] Document is consistent and well-formatted

### Testing Instructions

```
- Environment: macOS Sequoia
- Virtual environment: MUST use the existing .venv in the project root
- Activate venv: source .venv/bin/activate
- Review README.md for completeness and accuracy
- Verify all referenced commands work correctly
```

### Dependencies

- **Depends on:** Phase 5 (all testing complete)
- **Parallel with:** Task 6.1

### Constraints

```
- You must ONLY perform the actions in this task
- Do not make assumptions beyond the task scope
- Ask clarifying questions if anything is unclear
- You MUST create a plan before writing
- Keep user-facing docs clear and beginner-friendly
- Ensure all examples are accurate and tested
```

### Critical Files

- `README.md`

---

# Execution Order Summary

## Sequential Tasks (Must complete in order)

1. **Phase 1:** 1.1 → 1.2 → 1.3
2. **Phase 3:** 3.1 → 3.2 (then 3.3, 3.4 can be parallel)
3. **Phase 4:** 4.1 → 4.2 → 4.3
4. **Phase 5:** 5.1 → 5.2

## Parallel Task Groups

### After Task 1.3 completes:
- Tasks 2.1, 2.2, 2.3, 2.4, 2.5a, 2.5b can run in parallel

### After Tasks 2.1-2.5b complete:
- Tasks 2.6, 2.7 can run in parallel

### After Task 3.1 completes:
- Tasks 3.3, 3.4 can run in parallel (3.2 must be sequential)

### After Phase 5 completes:
- Tasks 6.1, 6.2 can run in parallel

---

# Breaking Changes Summary

This refactoring introduces breaking changes:

1. **Platform field required**: All pypeline projects must have `platform` set in `[tool.pypeline]`
2. **No automatic migration**: Existing projects must manually add platform field
3. **Dependencies structure**: `dependencies.py` now has `BASE_DEPENDENCIES` (platform-specific)
4. **Credentials structure**: `credentials.py.example` now platform-specific
5. **Utils file naming**: `platform_utils_file` replaces `snowflake_utils_file` property

**Migration Path for Existing Projects:**
Users must manually add to their `pyproject.toml`:
```toml
[tool.pypeline]
managed = true
platform = "snowflake"  # Add this line
```
