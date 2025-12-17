# **Pipeline CLI - Complete Project Plan**

---

## **Project Overview**

**Name:** Pipeline CLI  
**Tagline:** "Scaffolding framework for data pipeline projects"  
**Description:** A command-line tool that generates and maintains boilerplate code for data pipelines, allowing developers to focus on business logic while the CLI handles project structure, processor wiring, and orchestration.

**Value Proposition:**
- ⚡ Generate production-ready pipeline structure in 2 minutes
- 🔧 Maintain processor chains automatically via DAG
- 🔌 Plugin system for date strategies, platforms, and execution logic
- 🔒 Lock system prevents accidental overwrites of custom code
- 📦 Framework-agnostic with built-in support for Snowflake, Pandas, Spark

---

## **Phase 1: MVP (Minimum Viable Product) - 4-6 weeks**

### **Goal:** Core functionality working end-to-end with basic plugins

### **Deliverables:**

#### **1.1 Core CLI Commands (Week 1-2)**
- [ ] `init` - Initialize project configuration
- [ ] `pipeline create` - Create new pipeline
- [ ] `pipeline list` - List all pipelines
- [ ] `pipeline delete` - Delete pipeline
- [ ] `processor create` - Create processor (interactive + non-interactive)
- [ ] `processor list` - List processors in pipeline
- [ ] `processor delete` - Delete processor
- [ ] `rebuild` - Regenerate runner.py
- [ ] `validate` - Validate pipeline structure

**Tech Stack:**
- CLI framework: `typer` + `rich` (for beautiful output)
- Prompts: `questionary` (for interactive mode)
- Templating: `jinja2`

**Key Files to Build:**
```
src/pipeline_cli/
├── cli/
│   ├── main.py           # CLI entry point
│   ├── init.py           # init command
│   ├── pipeline.py       # pipeline commands
│   ├── processor.py      # processor commands
│   ├── rebuild.py        # rebuild command
│   └── validate.py       # validate command
```

#### **1.2 Configuration Management (Week 1)**
- [ ] `.pipeline_config.json` creation and management
- [ ] Config validation
- [ ] Path resolution (find config up directory tree)
- [ ] Pipeline metadata storage

**Key Files:**
```
src/pipeline_cli/core/
├── config_manager.py     # Manages .pipeline_config.json
└── file_operations.py    # File I/O utilities
```

#### **1.3 Code Generation (Week 2-3)**
- [ ] Template system using Jinja2
- [ ] Generate `config.py` (empty template)
- [ ] Generate `pipeline_config.py` (with plugin references)
- [ ] Generate `sequence.py` (DAG definition)
- [ ] Generate `runner.py` (complete orchestration)
- [ ] Generate processor templates

**Key Files:**
```
src/pipeline_cli/
├── core/
│   ├── pipeline_manager.py    # Pipeline CRUD
│   ├── processor_manager.py   # Processor CRUD
│   └── runner_generator.py    # Runner generation
└── templates/
    ├── pipeline/
    │   ├── config_py.jinja2
    │   ├── pipeline_config_py.jinja2
    │   ├── sequence_py.jinja2
    │   └── runner_py.jinja2
    └── processor/
        └── processor_py.jinja2
```

#### **1.4 DAG Management (Week 3)**
- [ ] Sequence manager (add/remove/reorder processors)
- [ ] DAG validation (detect cycles)
- [ ] Topological sort for execution order
- [ ] Parent-child relationship tracking

**Key Files:**
```
src/pipeline_cli/core/
├── sequence_manager.py   # Manages sequence.py
└── dag_validator.py      # Validates DAG
```

#### **1.5 Basic Plugin System (Week 4)**
- [ ] Plugin base classes (interfaces)
- [ ] 2-3 built-in date strategies:
  - `incremental` - Simple daily incremental
  - `rolling_window` - Last N days
  - `fixed_period` - Fixed date range
- [ ] 1 platform adapter:
  - `snowflake` - Snowflake/Snowpark (MVP)
- [ ] Plugin registry and loader

**Key Files:**
```
src/pipeline_cli/
├── plugins/
│   ├── base/
│   │   ├── date_strategy.py
│   │   └── platform.py
│   ├── date_strategies/
│   │   ├── incremental.py
│   │   ├── rolling_window.py
│   │   └── fixed_period.py
│   └── platforms/
│       └── snowflake.py
└── registry/
    ├── registry.py           # Plugin registry
    └── discovery.py          # Auto-discover plugins
```

#### **1.6 AST Manipulation (Week 4)**
- [ ] Parse existing runner.py
- [ ] Replace `_process_data()` method only
- [ ] Update processor imports
- [ ] Preserve custom code in other methods

**Key Files:**
```
src/pipeline_cli/utils/
└── ast_parser.py         # AST manipulation
```

#### **1.7 Testing Infrastructure (Week 5-6)**
- [ ] Unit tests for all core modules
- [ ] Integration test: full workflow (init → create → add processors → rebuild)
- [ ] Test fixtures and mocks
- [ ] CI/CD setup (GitHub Actions)

**Key Files:**
```
tests/
├── unit/
│   ├── test_config_manager.py
│   ├── test_pipeline_manager.py
│   ├── test_processor_manager.py
│   ├── test_runner_generator.py
│   └── test_dag_validator.py
├── integration/
│   └── test_full_workflow.py
└── fixtures/
    └── sample_configs/
```

#### **1.8 Documentation (Week 5-6)**
- [ ] README.md with quickstart
- [ ] Installation instructions
- [ ] Basic usage examples
- [ ] Command reference

---

## **Phase 2: Enhanced Features - 3-4 weeks**

### **Goal:** Add polish, more plugins, and advanced features

### **Deliverables:**

#### **2.1 Lock System (Week 7)**
- [ ] `runner lock <pipeline>` - Lock runner.py
- [ ] `runner unlock <pipeline>` - Unlock runner.py
- [ ] `runner status <pipeline>` - Check lock status
- [ ] Respect lock during `processor create`
- [ ] `--force` flag to override lock
- [ ] Lock metadata in config

**User Workflow:**
```bash
# Generate runner, then lock it
pipeline-cli rebuild beneficiary
pipeline-cli runner lock beneficiary

# Now safe to edit runner.py manually
# Future processor additions require --force or manual updates
```

#### **2.2 Additional Plugins (Week 7-8)**
- [ ] More date strategies:
  - `fiscal_period` - Fiscal quarters/years
  - `custom` - Placeholder that raises NotImplementedError
- [ ] More platform adapters:
  - `pandas` - Local Pandas DataFrames
  - `spark` - PySpark DataFrames
  - `generic` - Generic SQL adapter
- [ ] Execution strategies:
  - `sequential` - Default sequential execution
  - `conditional` - Template for conditional logic

#### **2.3 Finalize Command (Week 8)**
- [ ] Interactive workflow after processor development
- [ ] Validates all processors exist
- [ ] Checks plugins are configured
- [ ] Prompts to generate runner
- [ ] Prompts to lock runner if custom logic needed

```bash
pipeline-cli finalize beneficiary

# Interactive:
# ✓ Found 5 processors
# ✓ All files exist
# ? Generate runner.py? [Y/n]
# ? Lock runner after generation? [y/N]
```

#### **2.4 Configuration Commands (Week 8)**
- [ ] `config show` - Display pipeline config
- [ ] `config set --date-strategy <strategy>` - Update date strategy
- [ ] `config set --platform <platform>` - Update platform
- [ ] `config set --write-temp-tables <true|false>` - Toggle temp tables

#### **2.5 Better User Experience (Week 9)**
- [ ] Colored output with `rich`
- [ ] Progress indicators
- [ ] Better error messages
- [ ] Interactive confirmations for destructive operations
- [ ] `--verbose` flag for debugging

#### **2.6 Template Customization (Week 9-10)**
- [ ] Allow users to override default templates
- [ ] Custom template directory in config
- [ ] Template inheritance (extend built-in templates)

#### **2.7 Examples & Tutorials (Week 10)**
- [ ] Complete example projects:
  - `examples/basic_pipeline/` - Minimal ETL
  - `examples/branching_pipeline/` - Multiple branches
  - `examples/custom_plugins/` - Custom date strategy
- [ ] Step-by-step tutorials in docs

---

## **Phase 3: Advanced Features - 4-6 weeks**

### **Goal:** Production-ready with advanced workflows

### **Deliverables:**

#### **3.1 Multi-Parent Support (Week 11)**
- [ ] Processors can have multiple parents
- [ ] Pass multiple DataFrames to `process()` method
- [ ] Merge/join patterns in processor templates
- [ ] Update DAG validation for multi-parent

**Example:**
```python
PROCESSOR_SEQUENCE = [
    {"name": "base", "parents": []},
    {"name": "branch_a", "parents": ["base"]},
    {"name": "branch_b", "parents": ["base"]},
    {"name": "merger", "parents": ["branch_a", "branch_b"]},  # Multiple parents
]
```

#### **3.2 Plugin Marketplace (Week 12-13)**
- [ ] Plugin discovery system
- [ ] `plugin list` - List available plugins
- [ ] `plugin install <name>` - Install plugin from PyPI or Git
- [ ] `plugin publish` - Helper to publish plugins
- [ ] Community plugin registry (GitHub wiki or separate site)

#### **3.3 Testing Utilities (Week 13)**
- [ ] `test create <pipeline> <processor>` - Generate test stubs
- [ ] Mock data generators for processors
- [ ] Test runner for local-test mode

#### **3.4 DAG Visualization (Week 14)**
- [ ] `visualize <pipeline>` - Generate DAG diagram
- [ ] Output formats: PNG, SVG, Mermaid
- [ ] Use `graphviz` or `mermaid`

```bash
pipeline-cli visualize beneficiary --output dag.png
```

#### **3.5 Migration Tools (Week 14-15)**
- [ ] `migrate` - Update existing pipelines to new CLI version
- [ ] Detect and fix compatibility issues
- [ ] Backup before migration

#### **3.6 Conditional Execution Plugins (Week 15)**
- [ ] Execution strategy plugin with conditional logic
- [ ] Example: "Skip processor X in prod mode"
- [ ] Example: "Only run processor Y for certain file types"

#### **3.7 Performance Features (Week 16)**
- [ ] Parallel execution for independent branches
- [ ] Caching strategies (configurable via plugins)
- [ ] Lazy evaluation options

---

## **Phase 4: Polish & Release - 2-3 weeks**

### **Goal:** Production release with documentation and marketing

### **Deliverables:**

#### **4.1 Documentation (Week 17-18)**
- [ ] Complete user guide
- [ ] API reference
- [ ] Plugin development guide
- [ ] Architecture documentation
- [ ] FAQ
- [ ] Troubleshooting guide
- [ ] Video tutorials

**Documentation Site:**
- Use `mkdocs` + `mkdocs-material`
- Host on Read the Docs or GitHub Pages

#### **4.2 Packaging & Distribution (Week 18)**
- [ ] Publish to PyPI
- [ ] GitHub releases
- [ ] Changelog
- [ ] Version management strategy (semantic versioning)

#### **4.3 Marketing & Community (Week 19)**
- [ ] Blog post: "Introducing Pipeline CLI"
- [ ] Reddit posts (r/datascience, r/dataengineering, r/Python)
- [ ] Hacker News submission
- [ ] Twitter/LinkedIn announcements
- [ ] Create Discord or Slack community

#### **4.4 Real-World Testing (Week 19)**
- [ ] Use on 2-3 real projects
- [ ] Gather feedback
- [ ] Fix critical bugs
- [ ] Performance optimization

---

## **Technical Specifications**

### **Tech Stack**

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **CLI Framework** | Typer | Type-safe, auto-generates help, beautiful output |
| **Output Formatting** | Rich | Beautiful console output, tables, progress bars |
| **Prompts** | Questionary | Better than Click prompts, more intuitive |
| **Templating** | Jinja2 | Industry standard, powerful, familiar |
| **Testing** | Pytest | Best Python testing framework |
| **Code Quality** | Black + Ruff | Auto-formatting + fast linting |
| **Type Checking** | MyPy | Static type checking |
| **Documentation** | MkDocs Material | Beautiful, searchable docs |
| **CI/CD** | GitHub Actions | Free, well-integrated |

### **Dependencies (Minimal)**

**Core Dependencies:**
```
typer>=0.9.0          # CLI framework
rich>=13.0.0          # Beautiful output
jinja2>=3.1.0         # Templating
questionary>=2.0.0    # Interactive prompts
```

**Dev Dependencies:**
```
pytest>=7.0.0         # Testing
pytest-cov>=4.0.0     # Coverage
black>=23.0.0         # Formatting
ruff>=0.1.0           # Linting
mypy>=1.0.0           # Type checking
```

**Optional Dependencies:**
```
graphviz>=0.20.0      # For DAG visualization
snowflake-snowpark-python>=1.0.0  # For Snowflake plugin
pyspark>=3.0.0        # For Spark plugin
```

### **Python Version Support**

- **Minimum:** Python 3.8
- **Tested:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Recommended:** 3.10+

---

## **Development Workflow**

### **Git Workflow**

```
main (protected)
├── develop (default branch)
│   ├── feature/cli-commands
│   ├── feature/plugin-system
│   ├── feature/code-generation
│   └── feature/lock-system
└── release/v0.1.0
```

**Branch Naming:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `release/` - Release preparation

### **Commit Messages**

Use conventional commits:
```
feat: add processor create command
fix: resolve DAG circular dependency detection
docs: update quickstart guide
test: add integration tests for full workflow
refactor: simplify runner generation logic
```

### **Release Process**

1. Create release branch: `release/v0.1.0`
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md`
4. Run full test suite
5. Build package: `python -m build`
6. Test installation locally
7. Merge to `main`
8. Tag release: `git tag v0.1.0`
9. Push to PyPI: `twine upload dist/*`
10. Create GitHub release with notes

---

## **Testing Strategy**

### **Test Categories**

#### **1. Unit Tests (Fast, Isolated)**
```python
# Test individual components
def test_config_manager_creates_config():
    config = ConfigManager.create_initial_config(...)
    assert config.config_path.exists()

def test_dag_validator_detects_cycles():
    with pytest.raises(CircularDependencyError):
        validator.validate_dag(...)
```

#### **2. Integration Tests (End-to-End)**
```python
# Test complete workflows
def test_full_pipeline_creation_workflow(tmp_path):
    # Initialize
    run_cli(["init", "--pipelines-dir", str(tmp_path)])
    
    # Create pipeline
    run_cli(["pipeline", "create", "test_pipeline"])
    
    # Add processors
    run_cli(["processor", "create", "test_pipeline", "processor1"])
    
    # Validate
    assert (tmp_path / "test_pipeline" / "runner.py").exists()
```

#### **3. Smoke Tests (Real Usage)**
```python
# Test on real example projects
def test_basic_example_project():
    # Run full workflow on examples/basic_pipeline/
    # Ensure it generates correctly and runs without errors
```

### **Coverage Goals**

- **Core modules:** 90%+ coverage
- **CLI commands:** 80%+ coverage
- **Plugins:** 85%+ coverage
- **Overall:** 85%+ coverage

---

## **Documentation Structure**

```
docs/
├── index.md                    # Landing page
├── quickstart.md               # 5-minute tutorial
├── installation.md             # Install instructions
│
├── user-guide/
│   ├── concepts.md             # Core concepts (pipeline, processor, DAG, plugins)
│   ├── workflow.md             # Recommended workflow
│   ├── processor-development.md
│   ├── plugin-development.md
│   ├── lock-system.md
│   └── troubleshooting.md
│
├── cli-reference/
│   ├── init.md
│   ├── pipeline.md
│   ├── processor.md
│   ├── config.md
│   ├── runner.md
│   ├── rebuild.md
│   └── validate.md
│
├── api-reference/
│   ├── plugin-base-classes.md
│   ├── built-in-plugins.md
│   └── core-classes.md
│
└── examples/
    ├── simple-etl.md
    ├── branching-pipeline.md
    ├── custom-date-strategy.md
    └── multi-platform.md
```

---

## **Success Metrics**

### **Phase 1 (MVP) Success Criteria**
- [ ] Can create pipeline in under 2 minutes
- [ ] Can add 5 processors with correct wiring
- [ ] Generated runner.py executes without errors
- [ ] DAG validation catches circular dependencies
- [ ] At least 1 working built-in date strategy
- [ ] At least 1 working platform adapter (Snowflake)
- [ ] 80%+ test coverage
- [ ] Documentation covers all commands

### **Phase 2 Success Criteria**
- [ ] Lock system prevents accidental overwrites
- [ ] Finalize command provides smooth UX
- [ ] 3+ date strategies available
- [ ] 2+ platform adapters available
- [ ] Config management works smoothly
- [ ] Example projects run successfully

### **Phase 3 Success Criteria**
- [ ] Multi-parent processors work correctly
- [ ] Plugin marketplace discoverable
- [ ] DAG visualization generates clear diagrams
- [ ] Parallel execution (if implemented) shows performance gains

### **Phase 4 Success Criteria**
- [ ] Published to PyPI
- [ ] 100+ stars on GitHub
- [ ] 5+ community contributors
- [ ] Used in 3+ real projects
- [ ] Complete documentation
- [ ] Active community (Discord/Slack)

---

## **Risks & Mitigations**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **AST manipulation is complex** | High | Medium | Start simple, use well-tested libraries, extensive testing |
| **Plugin system too complicated** | Medium | Medium | Keep interfaces simple, provide clear examples |
| **User adoption is low** | High | Medium | Strong documentation, marketing, real-world examples |
| **Compatibility issues across Python versions** | Medium | Low | Test on multiple versions, use CI matrix |
| **Performance issues with large pipelines** | Low | Low | Optimize later, focus on correctness first |

---

## **Timeline Summary**

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 1: MVP** | 4-6 weeks | Core functionality + basic plugins |
| **Phase 2: Enhanced** | 3-4 weeks | Polish + more plugins + lock system |
| **Phase 3: Advanced** | 4-6 weeks | Multi-parent + marketplace + visualization |
| **Phase 4: Release** | 2-3 weeks | Documentation + packaging + marketing |
| **Total** | **13-19 weeks** | **~3-5 months** |

---

## **Initial Development Tasks (Week 1)**

### **Day 1-2: Project Setup**
- [ ] Create GitHub repository
- [ ] Set up project structure
- [ ] Configure `pyproject.toml`
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure Black, Ruff, MyPy
- [ ] Set up pre-commit hooks
- [ ] Create initial README

### **Day 3-4: Core CLI Framework**
- [ ] Implement `main.py` with Typer
- [ ] Implement `init` command
- [ ] Implement `ConfigManager`
- [ ] Add tests for init + ConfigManager
- [ ] Verify CLI runs: `python -m pipeline_cli init --help`

### **Day 5: Basic Pipeline Creation**
- [ ] Implement `pipeline create` command
- [ ] Implement `PipelineManager.create_pipeline()`
- [ ] Create basic Jinja2 templates
- [ ] Test pipeline creation end-to-end
- [ ] Verify: Can create empty pipeline structure

---

## **Post-Launch Roadmap (v1.1+)**

### **Features to Consider:**
- **Web UI** - Visual pipeline builder
- **Cloud integrations** - Deploy to Airflow/Prefect/Dagster
- **Data quality plugins** - Built-in data validation
- **Observability** - Metrics, tracing, alerting
- **Schema management** - Auto-generate table schemas
- **SQL templating** - Jinja2 for SQL queries
- **dbt integration** - Work with dbt projects
- **VS Code extension** - IDE integration

---

## **Call to Action**

**Next Steps:**
1. ✅ Review and approve this project plan
2. 🏗️ Set up GitHub repository
3. 🔧 Create initial project structure
4. 💻 Start Phase 1: Week 1 tasks
5. 🧪 Write first tests
6. 📝 Begin documentation

**Ready to start building?** Let's create the "Django for data pipelines"! 🚀

---

Would you like me to:
1. Create the initial `pyproject.toml` and project structure?
2. Write the first CLI command (`init`)?
3. Create template files for code generation?
4. Set up the test infrastructure?

Let me know where you want to start! 🎯