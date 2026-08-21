# Planner Framework - Quick Reference

## Installation

```bash
# Core
pip install pyyaml click networkx pydantic python-dateutil

# Web UI (optional)
pip install flask
# or: pip install lplan[web]
```

## CLI Commands

### Validate Plan
```bash
plan validate ./plan
# Checks: required fields, types, cross-references, design constraints
# Exit code 0 = valid, 1 = errors
```

### Analyze Priorities
```bash
plan priority ./plan
# Shows: project priority, computed score, drivers, mismatches
# ✓ = priority matches drivers, ✗ = mismatch (update priority)
```

### Show Project Dependencies
```bash
plan deps P001 ./plan
# Shows: what blocks P001, what P001 blocks, transitive deps
```

### List Blocked Projects
```bash
plan blocked ./plan
# Shows: all BLOCKED projects and their direct blockers
```

### Dependency Graph Report
```bash
plan graph-report ./plan
# Shows: total projects, dependencies, cycles, roots, leaves, cross-repo refs
```

### Show Statistics
```bash
plan stats ./plan
# Shows: project counts, % done, blocked count, priority mismatches
```

### Show Execution Timeline
```bash
plan timeline ./plan
# Shows: projects grouped by execution phase (what can run in parallel)
```

### Time Estimate Rollup
```bash
plan estimate ./plan
# Shows: total effort days, projects with/without estimates
```

### Velocity Analysis
```bash
plan velocity ./plan
# Shows: completed projects, actual vs estimated variance
```

### Log Entry
```bash
plan log P001 "Work in progress" ./plan
plan log P001 "Completed work" ./plan --status DONE
# Appends to entity's Log section, optionally updates status
```

### Update Entity
```bash
plan update P001 ./plan --status IN_PROGRESS
plan update P001 ./plan --priority HIGH
# Modifies frontmatter fields
```

### Generate Index
```bash
plan generate-index ./plan
# Regenerates INDEX.md from filesystem (repo name auto-detected from parent dir)
# Timestamp: "Last updated: YYYY-MM-DD HH:MM:SS UTC"
# Links use actual filenames, not title slugs — immune to title changes

plan generate-index ./plan --repo-name "MyProject"
# Override auto-detected repo name
```

### Web UI
```bash
plan serve ./plan                        # Read-only browser UI (port 8000)
plan serve ./plan --edit                 # Enable raw file editing
plan serve ./plan --port 9000            # Custom port
plan serve ./plan --edit --no-validate   # Skip validation on save
plan stop ./plan                         # Stop running server
plan restart ./plan                      # Restart with same options
# Server writes .plan-server.pid; stop/restart read it
```

### Initialize Plan
```bash
plan init ./new-plan --name "Project Name"
plan init ./new-plan --name "Project Name" --first-project "Initial Project"
# Creates: INDEX.md, FOCUS.md, CHANGELOG.md, REFLECTION.md, VALIDATION.md,
#          README.md, projects/, designs/, actions/
```

### Check References
```bash
plan check-refs ./plan
# Validates cross-references, flags orphaned entities, unused projects
```

### Governed Commit
```bash
plan commit ./plan -m "Updated project P001 status"
# Validates plan, stages changes, creates git commit (or reports validation errors)
```

### Generate HTML Report
```bash
plan report ./plan -o report.html
# Creates self-contained HTML with stats, tables, and SVG dependency graph
```

### Watch for Changes
```bash
plan watch ./plan
plan watch ./plan --interval 10
# Monitors plan directory, alerts on status changes, cycles, BLOCKED transitions
# (Ctrl-C to stop)
```

## Python API

### Parse Files
```python
from planner import PlanParser
from pathlib import Path

files = PlanParser.parse_directory(Path("plan/"))
for filepath, plan_file in files.items():
    print(f"{plan_file.entity.id}: {plan_file.entity.title}")
```

### Score Priorities
```python
from planner import PriorityEngine, Project

engine = PriorityEngine()
analysis = engine.analyze_project(project)

print(f"Score: {analysis['score']}")
print(f"Computed: {analysis['computed_priority']}")
print(f"Match: {analysis['match']}")
```

### Analyze Dependencies
```python
from planner import DependencyGraph

graph = DependencyGraph(projects)

# Blocking dependencies
blocking = graph.get_blocking_deps("P001")

# Impact analysis
impact = graph.impact_analysis("P001")
print(f"Unblocks: {impact['blocks']}")

# Cycle detection
if graph.has_cycles():
    print(f"Cycles: {graph.find_cycles()}")

# Execution order
order = graph.get_topological_order()
```

### Validate Schema
```python
from planner import SchemaValidator

validator = SchemaValidator()
if validator.validate_entity(project):
    print("Valid")

if validator.validate_relationships(entities):
    print("No broken refs")
```

## YAML Frontmatter Format

### Project
```yaml
---
id: P001
title: Project Title
status: PLANNING
priority: HIGH
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-20
depends:
  - P002
  - ltools:L001
enables:
  - P003
external_dependencies:
  - repo: external_sys
    feature: "Feature name"
    status: DONE
    blocking: false
estimate:
  effort_days: 5.0
  confidence: high
  started: 2026-08-20
  completed: 2026-08-25
---
```

**Estimate fields (all optional):**
- `effort_days`: Estimated effort in days (float)
- `confidence`: low | medium | high
- `started`: Date work started (ISO format)
- `completed`: Date work completed (ISO format)

### Design
```yaml
---
id: D001
title: Design Title
status: PLANNING
project: P001
created: 2026-08-20
updated: 2026-08-20
---
```

### Action
```yaml
---
id: A001
title: Task Title
status: IN_PROGRESS
design: D001
project: P001
priority: HIGH
created: 2026-08-20
updated: 2026-08-20
---
```

## Enums

### Status
`IDEA` | `PLANNING` | `IN_PROGRESS` | `BLOCKED` | `DONE` | `DEFERRED` | `CANCELLED`

### Priority
`HIGH` | `MEDIUM` | `LOW`

### Driver Weights (Core Framework)
| Driver | Weight |
|--------|--------|
| `critical_live_path_only` | +2.5 |
| `live_critical` | +2.0 |
| `improves_active` | +1.5 |
| `enables_multiple` | +1.5 |
| `strategic_edge` | +1.0 |
| `improves_accuracy` | +1.0 |
| `technical_debt` | +0.5 |
| `blocked_on_infrastructure` | -2.5 |
| `deferred_wait_*` | -2.0 |

### Priority Mapping
| Score | Priority |
|-------|----------|
| ≥ 2.0 | HIGH |
| 1.0–1.9 | MEDIUM |
| < 1.0 | LOW |

## File Structure
```
plan/
  INDEX.md          ← dashboard (auto-generated or hand-maintained)
  FOCUS.md          ← current active/blocked/next (rewritten each session)
  CHANGELOG.md      ← append-only status change log
  REFLECTION.md     ← append-only learnings, gotchas, patterns
  VALIDATION.md     ← validation workflow reference
  README.md         ← framework overview
  projects/
    P001-name.md
    P002-name.md
  designs/
    D001-name.md
  actions/
    A001-name.md
```

### FOCUS.md format (rewritten, not appended)
```markdown
## Active
What is being worked on right now.

## Blocked
What cannot proceed and why.

## Next
Ordered list of next 2–4 concrete steps.
```

### REFLECTION.md format (append-only)
```
YYYY-MM-DD | CATEGORY | insight text
```
Categories: `GOTCHA` · `PATTERN` · `LEARNING` · `WARNING` · `DECISION`

## Common Patterns

### Check What Blocks Progress
```bash
plan blocked plan/
# Shows all BLOCKED projects + direct blockers
```

### Find Critical Projects
```bash
plan graph-report plan/
# Look for projects with high fan-in (many dependents)
```

### Validate Before Commit
```bash
#!/bin/bash
plan validate plan/ || exit 1
plan graph-report plan/ | grep -q "Cycles: No" || exit 1
```

### Compute Priorities Programmatically
```python
from planner import *
from pathlib import Path

files = PlanParser.parse_directory(Path("plan/"))
engine = PriorityEngine()

for plan_file in files.values():
    if hasattr(plan_file, 'entity') and plan_file.entity.__class__.__name__ == 'Project':
        analysis = engine.analyze_project(plan_file.entity)
        if not analysis['match']:
            print(f"{analysis['project_id']}: update priority")
```

### Find Transitive Dependencies
```python
from planner import *

graph = DependencyGraph(projects)
transitive = graph.get_transitive_deps("P001")
print(f"P001 depends on (transitively): {transitive}")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Set `PYTHONPATH=src` or `PYTHONPATH=/path/to/lplan/src` |
| "Referenced project not found" | Check project exists: `find plan/ -name "*P999*"` or it's cross-repo (`repo:P999`) |
| Priority mismatch | Run `plan priority`, update priority field to match computed |
| Cycles detected | Run `plan graph-report`, break circular dependency |
| Slow validation | Check for very large `plan/` directory, validate subdirs separately |

## Example: Complete Workflow

```bash
# 1. Validate structure
plan validate plan/

# 2. Check priorities
plan priority plan/

# 3. Find what blocks progress
plan blocked plan/

# 4. Drill into specific dependency
plan deps P001 plan/

# 5. Full analysis
plan graph-report plan/
```

## Environment Setup

### Bash
```bash
# .bashrc or .zshrc
export PYTHONPATH="/path/to/lplan/src:${PYTHONPATH}"
alias plan="python3 -m planner.cli"
```

### Python Script
```python
import sys
sys.path.insert(0, '/path/to/lplan/src')
from planner import *
```

### CI/CD (.github/workflows/validate.yml)
```yaml
- name: Validate plan
  run: |
    pip install pyyaml click networkx pydantic python-dateutil
    PYTHONPATH=src python3 -m planner.cli validate plan/
    PYTHONPATH=src python3 -m planner.cli graph-report plan/ | grep -q "Cycles: No"
```

---

**Need more?** See MIGRATION.md for detailed guide or IMPLEMENTATION.md for architecture.
