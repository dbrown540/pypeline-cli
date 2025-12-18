# pypeline-cli

A command-line tool that generates and maintains boilerplate code for data pipelines, allowing developers to focus on business logic while the CLI handles project structure, dependency management, and scaffolding.

## Features

- 🚀 **Quick Project Setup** - Generate a complete data pipeline project structure in seconds
- 📦 **Smart Dependency Management** - Maintain dependencies in a user-friendly Python file
- 🔄 **Git Integration** - Automatic repository initialization with proper configuration
- 📝 **14 License Types** - Choose from MIT, Apache, GPL, and more
- 🏗️ **Opinionated Templates** - Pre-configured ETL structure with Snowflake support
- 🔧 **Virtual Environment Management** - Automated venv creation and dependency installation

## Installation

### Using pipx (Recommended)

```bash
pipx install pypeline-cli
```

### From Source

```bash
git clone https://github.com/dbrown540/pypeline-cli.git
cd pypeline-cli
pipx install -e .
```

## Quick Start

Create a new pipeline project:

```bash
pypeline init \
  --name my-etl-project \
  --author-name "Your Name" \
  --author-email "you@example.com" \
  --description "My data pipeline" \
  --license mit
```

Navigate to your project and install dependencies:

```bash
cd my-etl-project
pypeline install
```

## Commands

### `pypeline init`

Creates a new data pipeline project with a complete structure.

**Options:**
- `--destination` - Where to create the project (default: current directory)
- `--name` - Project name (required)
- `--author-name` - Author name (required)
- `--author-email` - Author email (required)
- `--description` - Project description (required)
- `--license` - License type (required)
  - Available: `mit`, `apache-2.0`, `gpl-3.0`, `gpl-2.0`, `lgpl-2.1`, `bsd-2-clause`, `bsd-3-clause`, `bsl-1.0`, `cc0-1.0`, `epl-2.0`, `agpl-3.0`, `mpl-2.0`, `unlicense`, `proprietary`
- `--company-name` - Company/organization name (optional, for license)

**What it creates:**
```mermaid
graph TD
    A[pypeline init] --> B[Create project directory]
    B --> C[Initialize git repository]
    C --> D[Create .gitattributes]
    D --> E[Create pyproject.toml]
    E --> F[Create dependencies.py]
    F --> G[Create LICENSE file]
    G --> H[Create folder structure<br/>src/project_name/pipelines/<br/>src/project_name/schemas/<br/>src/project_name/utils/<br/>tests/]
    H --> I[Create utilities in utils/<br/>databases.py, tables.py<br/>etl.py, date_parser.py]
    I --> J[Create .gitignore & README]
    J --> K[Commit to git]
```

**Project Structure Created:**
- Complete project structure with src-layout
- `pyproject.toml` with hatch-vcs for versioning
- Git repository with initial commit
- Template files for common data pipeline components
- License file
- `.gitignore` and `.gitattributes`

### `pypeline install`

Creates a virtual environment and installs project dependencies.

**Usage:**
```bash
cd your-project
pypeline install
```

**What it does:**
- Creates `.venv` directory
- Installs the project in editable mode
- Installs all dependencies from `pyproject.toml`

### `pypeline sync-deps`

Synchronizes dependencies from `dependencies.py` to `pyproject.toml`.

**Usage:**
```bash
pypeline sync-deps
```

**Why use this?**
- Edit dependencies in a user-friendly Python file (`dependencies.py`)
- Automatically updates `pyproject.toml` with proper formatting
- Validates dependency specifications

## Generated Project Structure

When you run `pypeline init`, it creates:

```
my-etl-project/
├── src/
│   └── my_etl_project/
│       ├── __init__.py
│       ├── _version.py          # Auto-generated from git tags
│       ├── pipelines/           # Your pipeline implementations
│       ├── schemas/             # Data schema definitions
│       └── utils/               # Utility modules (created here)
│           ├── databases.py     # USER EDITABLE - Database constants
│           ├── tables.py        # USER EDITABLE - Table configurations
│           ├── etl.py           # FRAMEWORK - Snowpark session manager
│           └── date_parser.py   # FRAMEWORK - DateTime utilities
├── tests/                       # Integration tests
├── dependencies.py              # USER EDITABLE - Manage dependencies here
├── pyproject.toml               # Project configuration
├── LICENSE                      # Your chosen license
├── README.md                    # Project readme
└── .gitignore                   # Python gitignore
```

### Understanding the Templates

#### 📝 `dependencies.py` (USER EDITABLE)

This is where you manage your project dependencies in a simple Python list:

```python
DEFAULT_DEPENDENCIES = [
    "snowflake-snowpark-python>=1.42.0",
    "pandas>=2.2.0",
    "python-dotenv>=1.0.0",
]
```

**Workflow:**
1. Edit `dependencies.py` to add/remove/update packages
2. Run `pypeline sync-deps` to update `pyproject.toml`
3. Run `pypeline install` to install new dependencies

#### 🗄️ `databases.py` (USER EDITABLE)

Define your database and schema constants:

```python
class Database:
    RAW = "RAW_DB"
    STAGING = "STAGING_DB"
    PROD = "PROD_DB"

class Schema:
    LANDING = "LANDING"
    TRANSFORM = "TRANSFORM"
```

#### 📊 `tables.py` (USER EDITABLE)

Manage dynamic table names with built-in date handling:

```python
from tables import TableConfig

# Create monthly partitioned table
config = TableConfig(
    base_name="sales_data",
    table_type="MONTHLY",
    date=datetime(2024, 3, 15)
)
table_name = config.table_name  # "SALES_DATA_202403"
```

**Table Types:**
- `YEARLY` - Appends year (e.g., `TABLE_2024`)
- `MONTHLY` - Appends year+month (e.g., `TABLE_202403`)
- `STABLE` - No date suffix (e.g., `TABLE`)

#### ⚙️ `etl.py` (FRAMEWORK - DO NOT MODIFY)

Singleton class for Snowpark session management:

```python
from etl import ETL

# Get Snowpark session
session = ETL.get_session()
df = session.table("MY_TABLE")
```

**Features:**
- Singleton pattern ensures one session per process
- Automatic connection management
- Environment variable configuration

#### 📅 `date_parser.py` (FRAMEWORK - DO NOT MODIFY)

Timezone-aware datetime utilities:

```python
from date_parser import DateTimeManager

dtm = DateTimeManager()

# Parse and normalize to UTC
dt = dtm.parse("2024-03-15 14:30:00", "%Y-%m-%d %H:%M:%S")

# Format for different uses
dtm.format_for_snowflake(dt)  # "2024-03-15 14:30:00"
dtm.format_for_filename(dt)   # "20240315_143000"
```

## Dependency Management Workflow

pypeline-cli uses a unique approach to dependency management:

```mermaid
graph LR
    A[Edit dependencies.py] --> B[pypeline sync-deps]
    B --> C[Updates pyproject.toml]
    C --> D[pypeline install]
    D --> E[Dependencies installed]
```

**Why this approach?**
- **User-Friendly**: Edit a simple Python list, not TOML
- **Version Control**: Track dependency changes in readable format
- **Validation**: Automatic validation of version specifications
- **Automation**: CLI handles TOML formatting

## Development Workflow

### 1. Create Project
```bash
pypeline init --name my-pipeline --author-name "Me" \
  --author-email "me@example.com" \
  --description "My pipeline" --license mit
```

### 2. Add Dependencies
Edit `src/my_pipeline/dependencies.py`:
```python
DEFAULT_DEPENDENCIES = [
    "snowflake-snowpark-python>=1.42.0",
    "pandas>=2.2.0",
    "requests>=2.31.0",  # Added
]
```

### 3. Sync and Install
```bash
pypeline sync-deps
pypeline install
```

### 4. Develop Your Logic
- Edit `databases.py` for your database structure
- Edit `tables.py` for your table configurations
- Create your ETL scripts using the provided utilities
- Use `ETL.get_session()` for Snowpark operations

### 5. Version and Release
```bash
git add .
git commit -m "Add feature"
git tag -a v0.1.0 -m "Initial release"
git push origin main --tags
```

Version is automatically determined from git tags via hatch-vcs.

## Project Configuration

### pyproject.toml

Generated projects use:
- **Build System**: hatchling with hatch-vcs
- **Python Version**: >=3.10 (Snowflake compatible)
- **Versioning**: Git tag-based (no manual version management)

### Git Configuration

Automatic initialization with:
- `core.autocrlf=input` for consistent line endings
- `.gitattributes` for cross-platform compatibility
- Initial commit with project structure

## Requirements

- Python 3.10+
- Git (for version management)
- pipx (recommended for installation)

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## Support

- GitHub Issues: https://github.com/dbrown540/pypeline-cli/issues
- PyPI: https://pypi.org/project/pypeline-cli/ 
