# Architecture: Programmatic Planning Engine

The Python execution engine behind lplan — typed, programmatic analysis of projects, dependencies, and priorities.

## Architecture

### Core Components

#### 1. **Data Models** (`src/planner/models.py`)
Typed Pydantic models representing plan entities:
- **Project** — high-level goals with priority, drivers, dependencies
- **Design** — specifications for projects
- **Action** — concrete tasks (for designs or projects)
- **PlanEntity** — base class with common validation
- **Status**, **Priority** — typed enums

Key validations:
- ID format (P001, D001, A001 with letter prefix + digits)
- Date ordering (updated >= created)
- Priority drivers must be non-empty
- Designs cannot be BLOCKED

#### 2. **Priority Scoring Engine** (`src/planner/priority.py`)
Computes priority from drivers using the framework definition:

```python
engine = PriorityEngine()
score = engine.compute_score(["critical_live_path_only", "improves_active"])
# score = 2.5 + 1.5 = 4.0 → Priority.HIGH
```

**Core Drivers** (weights):
- `critical_live_path_only` (+2.5)
- `live_critical` (+2.0)
- `improves_active` (+1.5)
- `enables_multiple` (+1.5)
- `strategic_edge` (+1.0)
- `improves_accuracy` (+1.0)
- `technical_debt` (+0.5)
- `blocked_on_infrastructure` (-2.5)
- `deferred_wait_*` (-2.0 for pattern matches)

**Score → Priority Mapping**:
- ≥ 2.0 → HIGH
- 1.0–1.9 → MEDIUM
- < 1.0 → LOW
- < 0 → LOW (with status=BLOCKED for context)

Supports custom drivers per-repo via `PriorityEngine(custom_drivers={...})`.

#### 3. **Dependency Graph Analyzer** (`src/planner/graph.py`)
NetworkX-based graph resolver with:

```python
graph = DependencyGraph(projects)

# Cycle detection
if graph.has_cycles():
    cycles = graph.find_cycles()

# Direct/transitive dependencies
blocking_deps = graph.get_blocking_deps("P001")
transitive_deps = graph.get_transitive_deps("P001")

# Impact analysis
impact = graph.impact_analysis("P001")
print(f"{impact['blocks']}")  # Projects this one unblocks

# Execution order
order = graph.get_topological_order()  # None if cycles exist

# Critical path and roots/leaves
graph.find_roots()   # Projects with no dependencies
graph.find_leaves()  # Projects with no dependents

# Full report
report = graph.get_report()
```

**Graph semantics**:
- Edges point from dependent to dependency (P001 -> P002 means P001 depends on P002)
- In-degree: projects that depend on this one
- Out-degree: projects this one depends on
- Supports cross-repo refs (e.g., `ltools:L001`) as external nodes

#### 4. **File Parser** (`src/planner/parser.py`)
Reads markdown files with YAML frontmatter:

```python
from planner import PlanParser

# Parse single file
plan_file = PlanParser.parse_file(Path("plan/projects/P001-test.md"))
print(plan_file.entity.id)  # "P001"
print(plan_file.entity.priority)  # Priority.HIGH
print(plan_file.goal)  # Markdown text

# Parse directory
results = PlanParser.parse_directory(Path("plan/"))
for filepath, plan_file in results.items():
    if not isinstance(plan_file, dict):  # Not an error
        print(plan_file.entity.id)
```

Handles:
- YAML frontmatter extraction with date parsing
- Markdown section parsing (Goal, Scope, Linked, Tasks, Log)
- Entity type inference from ID prefix
- Graceful error handling with error reporting

#### 5. **Schema Validator** (`src/planner/validator.py`)
Validates entities against schema rules:

```python
from planner import SchemaValidator

validator = SchemaValidator()

# Validate single entity
if validator.validate_entity(project):
    print("Valid")

# Validate relationships across entities
if validator.validate_relationships(entities):
    print("All cross-refs valid")

# Get report
report = validator.get_report()
print(f"Errors: {report['error_count']}")
print(f"Valid: {report['valid']}")
```

Checks:
- Required fields present
- Enum values valid (Status, Priority)
- Date consistency
- Cross-entity references (local and cross-repo)
- Design project references
- Design BLOCKED status prohibition

#### 6. **CLI Interface** (`src/planner/cli.py`)
Click-based commands for end-user interaction:

```bash
# Validate entire plan
plan validate ./plan

# Show priority analysis
plan priority ./plan

# Show dependencies for a project
plan deps P001 ./plan

# List blocked projects
plan blocked ./plan

# Full dependency graph report
plan graph-report ./plan
```

**Commands**:

- **validate** — Schema validation with relationship checking
- **priority** — Priority scoring analysis with driver breakdown
- **deps** — Show direct/transitive dependencies and dependents
- **blocked** — List BLOCKED projects and their blockers
- **graph-report** — Dependency graph analysis (cycles, roots, leaves, cross-repo refs)

## Usage Examples

### 1. Compute Project Priority

```python
from planner import Project, PriorityEngine, Status, Priority
from datetime import date

project = Project(
    id="P005",
    title="HyperLiquid API Integration",
    status=Status.PLANNING,
    priority=Priority.HIGH,
    priority_drivers=["critical_live_path_only"],
    created=date(2026, 8, 20),
    updated=date(2026, 8, 20),
)

engine = PriorityEngine()
analysis = engine.analyze_project(project)

print(f"Score: {analysis['score']}")
print(f"Computed priority: {analysis['computed_priority']}")
print(f"Match declared: {analysis['match']}")
```

### 2. Analyze Project Dependencies

```python
from planner import PlanParser, DependencyGraph
from pathlib import Path

# Parse all projects
files = PlanParser.parse_directory(Path("plan/"))
projects = {
    pf.entity.id: pf.entity 
    for pf in files.values() 
    if hasattr(pf, 'entity')
}

# Build graph
graph = DependencyGraph(projects)

# Find what P001 unblocks
dependents = graph.get_blocked_by("P001")
print(f"P001 unblocks: {dependents}")

# Check critical path
if not graph.has_cycles():
    order = graph.get_topological_order()
    print(f"Execution order: {order}")
else:
    print(f"Cycles detected: {graph.find_cycles()}")
```

### 3. Custom Priority Drivers

```python
from planner import PriorityEngine

# Add domain-specific drivers
custom = {
    "regulatory_compliance": 2.0,
    "backtest_validation": 1.0,
}

engine = PriorityEngine(custom_drivers=custom)
score = engine.compute_score(["regulatory_compliance"])  # 2.0
```

### 4. Validation with Relationship Checking

```python
from planner import SchemaValidator

validator = SchemaValidator()

# Validate individual entities
for entity in [proj1, proj2, design1]:
    if not validator.validate_entity(entity):
        for err in validator.errors:
            print(f"Error: {err}")

# Validate cross-references
entities = {"P001": proj1, "P002": proj2, "D001": design1}
validator.validate_relationships(entities)

for warning in validator.warnings:
    print(f"Warning: {warning}")
```

## Test Coverage

58 comprehensive tests covering:

- **Models** (15 tests)
  - Entity creation and validation
  - ID format and date constraints
  - Project/Design/Action-specific rules

- **Priority** (14 tests)
  - Score computation from drivers
  - Priority mapping
  - Custom driver support
  - Mismatch detection

- **Dependency Graph** (13 tests)
  - Cycle detection
  - Path finding and transitive closure
  - Root/leaf identification
  - Cross-repo reference handling
  - Topological ordering

- **Parser** (8 tests)
  - YAML frontmatter extraction
  - Markdown section parsing
  - Date parsing and validation
  - Error handling

- **Validator** (8 tests)
  - Entity validation
  - Relationship checking
  - Cross-repo reference validation

Run tests:
```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```

## Key Differences from Shell Scripts

| Aspect | Old (Shell) | New (Python) |
|--------|------------|------------|
| Validation | Pattern matching | Full schema validation with Pydantic |
| Priority | Manual documentation | Programmatic computation with scoring |
| Dependencies | Declared but not analyzed | Full graph analysis (cycles, paths) |
| Queries | Read-only inspection | Structured queries (deps, impact, blocking) |
| Type Safety | None | Full type hints + validation |
| Testing | Manual | 58 automated tests |
| Extensibility | Hard to modify | Pluggable drivers, custom validators |

## Next Steps (Tier 2 & 3)

### Tier 2 — Analysis & Query Tools
- Burndown/progress tracking
- Impact matrix generation
- Bottleneck detection (high fan-in/out)
- Dependency depth metrics

### Tier 3 — Automation & Visualization
- Pre-commit hooks for validation
- Auto-update of cross-repo refs
- Dependency graph visualization (Mermaid/Graphviz)
- Status propagation when dependencies complete
- Gantt chart generation (with time estimates)

## Installation & Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov

# Run CLI
PYTHONPATH=src python3 -m planner.cli validate ./plan
```

## Architecture Notes

- **Pydantic models** ensure schema compliance at parse time, not just in validation
- **NetworkX** handles graph analysis (cycles, paths, topological sort)
- **Click** provides CLI without external dependencies for scripting
- **Type hints** throughout enable IDE support and static type checking
- **Test fixtures** use temporary directories to avoid side effects
