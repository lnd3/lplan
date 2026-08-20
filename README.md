# Planner Framework

A generic, reusable planning system for organizing projects, designs, and actions across software repositories. Supports hierarchical linking to submodules and cross-repo dependencies.

## Overview

This framework defines:
- **Schema**: Valid structure for projects, designs, actions, and indices
- **Templates**: Boilerplate files for instantiating in any repository
- **Tools**: Scripts to validate, aggregate, and link hierarchically
- **Examples**: Reference implementations

## Quick Start

### Using the Python Engine (Recommended)

```bash
# 1. Install dependencies
pip install pyyaml click networkx pydantic python-dateutil

# 2. Use the wrapper script (no PYTHONPATH setup needed)
./bin/plan validate ./plan
./bin/plan priority ./plan

# 3. Or set up an alias for convenience
alias plan="./bin/plan"
plan deps P001 ./plan
plan graph-report ./plan

# 4. Or export PYTHONPATH
export PYTHONPATH="${PWD}/src"
python3 -m planner.cli validate ./plan
```

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more commands.

### Initialize a New Plan

```bash
# In your repo root:
./bin/plan init ./plan --name "MyProject"

# This creates:
# plan/
#   INDEX.md
#   CHANGELOG.md
#   projects/P001-*.md (template)
#   designs/
#   actions/
```

### Define a Project

1. Edit `plan/projects/P001-*.md` with your project details
2. Fill in frontmatter according to `schema/project.schema.md`
3. Run validation: `./bin/plan validate ./plan`

### Link Submodules

If your repo has git submodules with their own `plan/` directories:

```bash
# Submodules auto-discovered
./tools/aggregate-local.sh

# Generates hierarchical view:
# - Local projects (P001–P007)
# - Linked submodules (deps/ltools/plan/, deps/ldeps/plan/)
# - Cross-repo dependencies
```

### Migrating from Shell Scripts?

If you're currently using the shell-based `validate.sh`, see [MIGRATION.md](MIGRATION.md) for a step-by-step guide.

## Structure

- **schema/** — Formal definitions and specs
- **templates/** — Boilerplate files
- **tools/** — Validation, aggregation, initialization scripts
- **examples/** — Reference implementations

## Documentation

### For Users

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Cheat sheet for CLI commands and Python API
- **[MIGRATION.md](MIGRATION.md)** — Step-by-step guide from shell scripts to Python engine
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Detailed issue resolution and debugging

### For Developers

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** — Architecture, data models, and extension points
- **[pyproject.toml](pyproject.toml)** — Python dependencies and build configuration
- **[tests/](tests/)** — 58 comprehensive test cases covering all components

### Schema Reference

See `schema/` for formal specifications:
- `frontmatter.md` — YAML frontmatter format and fields
- `project.schema.md` — Project file structure
- `design.schema.md` — Design file structure
- `action.schema.md` — Action file structure
- `index.schema.md` — INDEX.md structure and generation rules
- `priority-framework.md` — Driver definitions and scoring
- `aggregation-rules.md` — How hierarchical linking works

## Tools

### Python Engine (New — Recommended)
Modern programmatic approach with full dependency analysis and priority scoring:

```bash
# Install
pip install pyyaml click networkx pydantic python-dateutil

# Validate plan
plan validate ./plan

# Analyze priorities
plan priority ./plan

# Show dependencies
plan deps P001 ./plan

# Full dependency graph analysis
plan graph-report ./plan
```

**Why the Python engine?**
- ✅ Programmatic priority computation (no manual scoring)
- ✅ Full dependency graph analysis (cycle detection, critical path)
- ✅ Type-safe validation with Pydantic
- ✅ Structured queries and impact analysis
- ✅ 58 comprehensive test suite

### Shell Scripts (Legacy)
Original bash-based validation (still works, no longer developed):

- `tools/validate.sh` — Check a plan/ directory against schema
- `tools/aggregate-local.sh` — Scan for submodules and generate hierarchical INDEX
- `tools/init-repo.sh` — Initialize plan/ in a new repo

## Installation & Updates

Install lplan in your project:

```bash
# Clone or add as a dependency
git clone https://github.com/yourusername/lplan /path/to/lplan

# Install dependencies
pip install -r /path/to/lplan/requirements.txt

# Create alias for convenience
alias plan="/path/to/lplan/bin/plan"
```

## Core Concepts

### Project Planning
Organize work into hierarchical projects (goals), designs (specs), and actions (tasks). Use structured YAML + markdown for both machine readability and human editing.

### Dependency Tracking
Declare explicit dependencies between projects. lplan analyzes them to find cycles, compute critical paths, and show execution order.

### Priority Scoring
Automatically compute project priority from weighted drivers. Detect mismatches between driver score and declared priority.

### Multi-Repo Support
Use cross-repo references to link plans across dependencies. Example: `depends: ["upstream-lib:UP001"]`

## Multi-Repo Planning

```
my-app/
  plan/                       ← Local projects for my-app
    projects/P001-*.md
    designs/D001-*.md
    actions/A001-*.md

deps/upstream-lib/plan/       ← Linked submodule (upstream-lib)
  projects/UP001-*.md

deps/shared-tools/plan/       ← Linked submodule (shared-tools)
  projects/ST001-*.md
```

Use cross-repo references in dependencies: `depends: ["upstream-lib:UP001"]`

## Development

To contribute to lplan:

1. Clone the repository
2. Make changes to `src/planner/` modules
3. Run tests: `PYTHONPATH=src pytest tests/ -v`
4. Test manually: `./bin/plan <command> plan/`
5. Update docs if needed
6. Commit and create a pull request

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for architecture details.
