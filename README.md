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

### Instantiate in a Repository

```bash
# In your repo root:
cp -r /path/to/planner-framework/.planner-framework .
./tools/init-repo.sh --name "MyProject" --role "Core system"

# This creates:
# plan/
#   README.md
#   INDEX.md
#   CHANGELOG.md
#   projects/
#   designs/
#   actions/
```

### Define a Project

1. Copy `planner-framework/templates/project.md.template` to `plan/projects/P001-my-project.md`
2. Fill in frontmatter according to `schema/project.schema.md`
3. Run validation: `plan validate ./plan`

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

## Versioning

Each repo instantiates a specific version of planner-framework via git submodule. Update .planner-framework to get framework updates:

```bash
cd .planner-framework && git pull origin main
cd ..
git add .planner-framework && git commit -m "Update planner-framework"
```

## Concepts

### Repo-Scoped Plans
Each repository has its own `plan/` directory following this framework. Plans are independent; each repo owns its projects, designs, and actions.

### Hierarchical Linking
Submodules with their own `plan/` are automatically discovered. Cross-repo dependencies are resolved and displayed in aggregated views (e.g., "P005 depends on ltools:L001").

### Independent Instances
Multiple repos can use planner-framework without coordination. Each has its own frontmatter, priorities, and changelog. Aggregation is computed on-demand.

### Schema as Guarantee
All repos using the framework conform to the same schema. Tools can validate, traverse, and aggregate with certainty.

## Example: TradeFlow + Submodules

```
TradeFlow/
  .planner-framework/         ← git submodule (shared framework)
  plan/                       ← Instance 1 (TradeFlow strategy)
    INDEX.md                  ← Shows local + linked submodule work
    projects/P001-P007.md
  deps/ltools/plan/           ← Instance 2 (ltools infrastructure)
    INDEX.md                  ← Shows ltools work
    projects/L001-L005.md
  deps/ldeps/plan/            ← Instance 3 (ldeps build system)
    INDEX.md
    projects/D001-D003.md
```

Running `./tools/aggregate-local.sh` in TradeFlow root generates a hierarchical view showing all three plans linked together.

## Contributing

Framework updates are versioned. To propose changes:
1. Edit files in planner-framework/
2. Test in examples/
3. Update version in README.md
4. Commit and tag

Repos update via `git submodule update --remote`.
