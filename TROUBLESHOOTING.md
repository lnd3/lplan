# Troubleshooting Guide

## Installation Issues

### Python version mismatch

**Error:** `SyntaxError: invalid syntax` or `Unsupported Python version`

**Cause:** Planner requires Python 3.9+

**Solution:**
```bash
python3 --version  # Should be 3.9 or higher
# If not, use python3.x (e.g., python3.10)
python3.10 -m pip install pyyaml click networkx pydantic python-dateutil
PYTHONPATH=src python3.10 -m planner.cli --version
```

### Dependency installation fails

**Error:** `pip install` fails with version conflicts

**Cause:** Conflicting package versions in your environment

**Solution:**
```bash
# Option 1: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install pyyaml click networkx pydantic python-dateutil

# Option 2: Install specific versions
pip install pyyaml==6.0 click==8.1.0 networkx==3.0 pydantic==2.0 python-dateutil==2.8.2

# Option 3: Check pyproject.toml for exact versions
grep dependencies pyproject.toml
```

### `ModuleNotFoundError: No module named 'planner'`

**Cause:** PYTHONPATH not set or working directory wrong

**Solution:**
```bash
# Option 1: Set PYTHONPATH
export PYTHONPATH="/full/path/to/lplan/src:${PYTHONPATH}"
plan validate plan/

# Option 2: Run from repo root
cd /path/to/lplan
PYTHONPATH=src python3 -m planner.cli validate plan/

# Option 3: Check current directory
pwd  # Should be repo root
ls src/planner/  # Should list *.py files

# Option 4: Create permanent alias
echo 'alias plan="PYTHONPATH=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/src python3 -m planner.cli"' >> ~/.bashrc
source ~/.bashrc
```

## File Parsing Issues

### `ValueError: File ... does not start with frontmatter delimiter`

**Cause:** Plan file doesn't start with `---`

**Fix:**
```markdown
# WRONG - missing opening ---
id: P001
title: Test
---

# CORRECT
---
id: P001
title: Test
---

Content starts here
```

### `ValueError: Invalid YAML in ... : mapping values are not allowed here`

**Cause:** YAML indentation error

**Fix:**
```yaml
# WRONG - inconsistent indentation
priority_drivers:
  - strategic_edge
 - improves_active  # Extra space!

# CORRECT
priority_drivers:
  - strategic_edge
  - improves_active
```

### `ValueError: Frontmatter in ... is not a YAML object`

**Cause:** Frontmatter contains list or scalar instead of dict

**Fix:**
```yaml
# WRONG
---
- id: P001
- title: Test
---

# CORRECT
---
id: P001
title: Test
---
```

## Validation Issues

### `[P001] depends: Referenced project P002 not found`

**Cause:** Project P002 doesn't exist locally

**Diagnosis:**
```bash
# Check if file exists
find plan/ -name "*P002*"

# Check if it's cross-repo
grep -r "P002" plan/projects/P001*  # Look for cross-repo syntax (ltools:P002)

# List all projects
grep -h "^id:" plan/projects/*.md | sort
```

**Fix:**
```yaml
# Option 1: Create missing project
# Create plan/projects/P002-description.md

# Option 2: Fix reference if it's cross-repo
depends:
  - ltools:P002  # Cross-repo ref (external, OK)
  # Instead of: - P002

# Option 3: Remove invalid dependency if it's not needed
# Delete the problematic line from depends:
```

### `[D001] project: Parent project P001 not found`

**Cause:** Design D001 references missing parent project P001

**Fix:**
```yaml
# Option 1: Create parent project
# Create plan/projects/P001-*.md

# Option 2: Verify parent project exists
ls plan/projects/P001*

# Option 3: Update design with correct parent
# Edit D001 to reference an existing project
project: P002  # Change to existing project
```

### `[D001] status: Designs cannot have BLOCKED status`

**Cause:** Design has BLOCKED status (not allowed)

**Fix:**
```yaml
# WRONG
status: BLOCKED

# CORRECT - use IN_PROGRESS or DEFERRED instead
status: IN_PROGRESS

# Or deferred if waiting
status: DEFERRED
```

## Priority Issues

### Priority mismatch: `computed=HIGH but declared=MEDIUM`

**Cause:** Driver weights don't match declared priority

**Diagnosis:**
```bash
plan priority plan/ | grep "✗"  # Show all mismatches

# Or check specific project
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from planner import *
from pathlib import Path

files = PlanParser.parse_directory(Path("plan/"))
engine = PriorityEngine()

for plan_file in files.values():
    if hasattr(plan_file, 'entity'):
        if plan_file.entity.id == "P001":
            analysis = engine.analyze_project(plan_file.entity)
            print(f"Score: {analysis['score']}")
            print(f"Drivers: {analysis['driver_contributions']}")
            print(f"Computed: {analysis['computed_priority']}")
            print(f"Declared: {analysis['declared_priority']}")
EOF
```

**Fix:**
```yaml
# Option 1: Update priority to match drivers
priority_drivers:
  - critical_live_path_only  # +2.5 = HIGH
priority: HIGH  # Update from MEDIUM

# Option 2: Adjust drivers to match desired priority
# If you want MEDIUM (1.0-1.9), use lower-weight drivers
priority_drivers:
  - strategic_edge  # +1.0 = LOW, need 1+ more
  - improves_accuracy  # +1.0 = MEDIUM
priority: MEDIUM

# Option 3: Document the mismatch in Log section
---
## Log
2026-08-20 — Priority MEDIUM kept despite HIGH driver score
           Due to external blocker P005, not on critical path
```

### Unknown driver warning: `⚠️ Unknown drivers: regulatory_compliance`

**Cause:** Driver not in core framework or not registered

**Fix:**
```python
# Option 1: Use core framework drivers
priority_drivers:
  - technical_debt  # Use core driver

# Option 2: Register custom driver
from planner import PriorityEngine

custom = {"regulatory_compliance": 2.0}
engine = PriorityEngine(custom_drivers=custom)

# Option 3: Document in project README
# Define custom drivers in PRIORITY_DRIVERS.md
```

## Dependency Graph Issues

### `Cycles detected`

**Error:** `plan graph-report` shows cycles

**Diagnosis:**
```bash
plan graph-report plan/
# Output: Cycles detected (1):
#   P001 → P002 → P001

# Or programmatically
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from planner import *
from pathlib import Path

files = PlanParser.parse_directory(Path("plan/"))
projects = {pf.entity.id: pf.entity for pf in files.values() if hasattr(pf, 'entity')}
graph = DependencyGraph(projects)

for cycle in graph.find_cycles():
    print(f"Cycle: {' → '.join(cycle)} → {cycle[0]}")
EOF
```

**Fix:**
```yaml
# Step 1: Identify the cycle (e.g., P001 ← P002 ← P001)
# Step 2: Check if dependencies are truly needed
# Step 3: Break the cycle - several strategies:

# Strategy A: Remove unnecessary dependency
# In projects/P002.md:
depends:
  # Remove: - P001  (if not truly needed)

# Strategy B: Add intermediate project to order phases
# Create P003 that both depend on:
# P002 depends on: P003
# P001 depends on: P003
# Remove: P002 → P001

# Strategy C: Change to enables relationship
# Instead of P002 depending on P001,
# Have P001 enable P002 (P001 should be done first)
```

### Topological order returns `None`

**Cause:** Cycles prevent ordering

**Fix:** See "Cycles detected" section above

### "Cross-repo ref not resolved: `ltools:P001`"

**Note:** Cross-repo refs are expected - they're external

**Info:**
```bash
plan graph-report plan/
# Look for "Cross-repo references" section
# These are allowed but not validated locally

# In a multi-repo aggregation setup, these would be resolved
```

## CLI Performance Issues

### `plan validate` is very slow

**Diagnosis:**
```bash
# Check plan size
find plan/ -name "*.md" | wc -l

# Time individual operations
time plan validate plan/projects/
time plan priority plan/projects/
time plan graph-report plan/projects/
```

**Cause:** Very large plan directory (1000+ files)

**Fix:**
```bash
# Option 1: Validate by subdirectory
plan validate plan/projects/
plan validate plan/designs/
plan validate plan/actions/

# Option 2: Filter to specific projects
# Create temporary filtered directory
mkdir /tmp/plan_subset
cp -r plan/{projects,designs,actions} /tmp/plan_subset/
plan validate /tmp/plan_subset/

# Option 3: Use Python API with profiling
python3 -m cProfile -s cumtime << 'EOF'
import sys
sys.path.insert(0, 'src')
from planner import PlanParser
from pathlib import Path

files = PlanParser.parse_directory(Path("plan/"))
print(f"Parsed {len(files)} files")
EOF
```

## Data Quality Issues

### Projects have same ID

**Error:** Duplicate project IDs

**Diagnosis:**
```bash
grep -h "^id:" plan/projects/*.md | sort | uniq -d
# Shows duplicate IDs
```

**Fix:**
```bash
# Find duplicates
grep -h "^id:" plan/projects/*.md | sort | uniq -c | grep -v "^ *1"

# Rename one to unique ID
mv plan/projects/P001-name1.md plan/projects/P009-name1.md
# Update ID inside file too
```

### Invalid date format

**Error:** `ValueError: time data '2026-8-20' does not match format '%Y-%m-%d'`

**Fix:**
```yaml
# WRONG - missing leading zeros
created: 2026-8-20

# CORRECT - ISO 8601 format with leading zeros
created: 2026-08-20
```

### Task list with wrong format

**Error:** Tasks not parsed correctly

**Diagnosis:**
```bash
grep -A5 "^## Tasks" plan/projects/P001*.md
```

**Fix:**
```markdown
# WRONG - missing space after bracket
- [x]Task 1
- [ ] Task 2

# CORRECT - space required
- [x] Task 1
- [ ] Task 2

# Or missing brackets altogether
- Done task  # Not recognized as task
- [ ] Pending task
```

### Log entries not parsed

**Cause:** Wrong date format or line structure

**Fix:**
```markdown
# CORRECT format for log entries
## Log

2026-08-20 — Brief description of what changed
2026-08-19 — Another entry

# WRONG - no date prefix
## Log
- Changed status
- Updated priority
```

## Debugging Tips

### Enable verbose output

```python
# Create debug script
import sys
sys.path.insert(0, 'src')
from planner import PlanParser
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

# Add debug output to model validation
from pydantic import BaseModel
BaseModel.model_rebuild()  # Force full validation

files = PlanParser.parse_directory(Path("plan/"))
print(f"Loaded {len(files)} files")

for filepath, result in files.items():
    if isinstance(result, dict) and 'error' in result:
        print(f"ERROR: {filepath}: {result['error']}")
    else:
        print(f"OK: {result.entity.id}")
```

### Inspect parsed data

```python
import sys
sys.path.insert(0, 'src')
from planner import PlanParser
from pathlib import Path
import json

plan_file = PlanParser.parse_file(Path("plan/projects/P001-test.md"))

# Show entity as dict
print(json.dumps(plan_file.entity.model_dump(), indent=2, default=str))

# Show sections
print(f"Goal: {plan_file.goal[:50]}...")
print(f"Scope: {plan_file.scope[:50]}...")
print(f"Tasks: {plan_file.tasks}")
print(f"Log: {plan_file.log}")
```

### Check imports work

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

try:
    from planner import Project, Design, Action
    print("✓ Models imported")
except Exception as e:
    print(f"✗ Models failed: {e}")

try:
    from planner import PriorityEngine
    print("✓ Priority engine imported")
except Exception as e:
    print(f"✗ Priority engine failed: {e}")

try:
    from planner import DependencyGraph
    print("✓ Graph imported")
except Exception as e:
    print(f"✗ Graph failed: {e}")

try:
    from planner import PlanParser
    print("✓ Parser imported")
except Exception as e:
    print(f"✗ Parser failed: {e}")

try:
    from planner import SchemaValidator
    print("✓ Validator imported")
except Exception as e:
    print(f"✗ Validator failed: {e}")
EOF
```

## Integration Issues

### Git pre-commit hook fails

**Setup:**
```bash
# Create .git/hooks/pre-commit
#!/bin/bash
export PYTHONPATH="${PWD}/src"
python3 -m planner.cli validate plan/ || exit 1

chmod +x .git/hooks/pre-commit
```

### CI/CD integration fails

**GitHub Actions:**
```yaml
- name: Validate plan
  run: |
    pip install pyyaml click networkx pydantic python-dateutil
    PYTHONPATH=src python3 -m planner.cli validate plan/
```

**GitLab CI:**
```yaml
validate_plan:
  image: python:3.10
  script:
    - pip install pyyaml click networkx pydantic python-dateutil
    - PYTHONPATH=src python3 -m planner.cli validate plan/
```

### Docker container validation

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install pyyaml click networkx pydantic python-dateutil
CMD ["sh", "-c", "PYTHONPATH=src python3 -m planner.cli validate plan/"]
```

## Performance Optimization

### Slow validation on large plans

```python
# Profile the validator
import cProfile
import sys
sys.path.insert(0, 'src')
from planner import PlanParser, SchemaValidator
from pathlib import Path

def validate_all():
    files = PlanParser.parse_directory(Path("plan/"))
    validator = SchemaValidator()
    for pf in files.values():
        if hasattr(pf, 'entity'):
            validator.validate_entity(pf.entity)

cProfile.run('validate_all()', sort='cumtime')
# Look for bottlenecks
```

### Cache parsed results

```python
from pathlib import Path
import pickle
import sys
sys.path.insert(0, 'src')
from planner import PlanParser

plan_path = Path("plan/")
cache_path = Path(".plan_cache.pkl")

if cache_path.exists():
    with open(cache_path, 'rb') as f:
        files = pickle.load(f)
else:
    files = PlanParser.parse_directory(plan_path)
    with open(cache_path, 'wb') as f:
        pickle.dump(files, f)

# Invalidate cache when plan changes
# (e.g., in pre-commit hook)
```

---

**Still stuck?** Check QUICK_REFERENCE.md (commands), IMPLEMENTATION.md (architecture), or tests/*.py (usage examples).
