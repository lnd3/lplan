# Migration Guide: From Shell Scripts to Python Engine

This guide helps you migrate from the original shell-based validation to the new programmatic Python engine.

## Overview

The Planner Framework is evolving from **instruction-based schemas + shell validation** to **programmatic analysis with semantic understanding**.

### What's Changing

| Layer | Old | New | Benefit |
|-------|-----|-----|---------|
| **Validation** | Bash pattern matching (`grep`) | Pydantic type checking | Catches errors at parse time, not read-time |
| **Priority** | Manual entry in YAML | Computed from drivers | Automatic detection of mismatches |
| **Dependencies** | Listed as strings | Graph analysis | Cycle detection, critical path, impact analysis |
| **Queries** | Manual file inspection | Programmatic APIs | Structured answers: "What blocks me?" |
| **Type Safety** | None | Full type hints | IDE autocomplete, static checking |

### What's NOT Changing

✓ **File format** — Still markdown with YAML frontmatter  
✓ **Schema structure** — Same fields (id, title, status, priority_drivers, etc.)  
✓ **Driver definitions** — Same core drivers and weights  
✓ **Directory layout** — Same `plan/projects/`, `plan/designs/`, `plan/actions/`

## Installation & Setup

### 1. Install Python Engine

```bash
# Install dependencies
pip install pyyaml click networkx pydantic python-dateutil

# Or from pyproject.toml
pip install -e .  # Once we add setup.py support
```

### 2. Verify Installation

```bash
# Test import
python3 -c "import sys; sys.path.insert(0, 'src'); from planner import PriorityEngine; print('✓ Installed')"

# Run tests
PYTHONPATH=src python3 -m pytest tests/ -v
```

### 3. Update Your Scripts

Replace old shell commands:

```bash
# Old
./tools/validate.sh plan/

# New
PYTHONPATH=src python3 -m planner.cli validate plan/
```

Or set up alias:

```bash
# .bashrc or .zshrc
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
alias plan="python3 -m planner.cli"

# Now use: plan validate plan/
```

## Migration Patterns

### Pattern 1: Validation

**Before:** Shell script with basic field checking
```bash
./tools/validate.sh plan/
# Output: Missing id field, Missing title, etc.
```

**After:** Semantic validation with relationship checking
```bash
plan validate plan/
# Validates:
# - Required fields present & typed correctly
# - Cross-references resolve (P001 depends on P002 → P002 exists)
# - Design statuses (no BLOCKED designs)
# - Date consistency
```

**Migration steps:**
1. Run new validator on your existing plan
2. Fix any relationship errors (missing cross-refs)
3. Verify design/action parent references
4. Update CI/CD to call new validator

### Pattern 2: Priority Scoring

**Before:** Manual entry in frontmatter
```yaml
priority_drivers:
  - strategic_edge
  - improves_active
priority: HIGH  # ← Manually entered
```

**After:** Computed from drivers; mismatch detection
```bash
plan priority plan/
```

Output:
```
✓ P001: HIGH   (score=  2.5, status=PLANNING)
  - strategic_edge       +1.0
  - improves_active      +1.5
✗ P002: MEDIUM (score=  2.0, status=PLANNING)  # Mismatch! Computed HIGH
  - critical_live_path   +2.5
  - technical_debt       +0.5
```

**Migration steps:**
1. Run `plan priority` on your plan
2. For any mismatches (✗), update the declared priority
3. Document if there's a reason to keep priority != computed (e.g., strategic value > executable readiness)
4. Add validation to CI to flag future mismatches

**Example: Fix Mismatches**
```python
# Programmatic approach
from planner import PlanParser, PriorityEngine

files = PlanParser.parse_directory(Path("plan/"))
engine = PriorityEngine()

for plan_file in files.values():
    if hasattr(plan_file, 'entity'):
        analysis = engine.analyze_project(plan_file.entity)
        if not analysis['match']:
            print(f"{analysis['project_id']}: "
                  f"update priority {analysis['declared_priority']} "
                  f"→ {analysis['computed_priority']}")
```

### Pattern 3: Dependency Analysis

**Before:** Declared but not analyzed
```yaml
# projects/P001.md
depends:
  - P002
  - tradeflow:P003
```

**After:** Full graph analysis
```bash
plan deps P001 plan/
```

Output:
```
Project: P001 - Core Strategy
======================================================================

Direct Dependencies (blocks this project):
  - P002: Infrastructure (DONE)
  - tradeflow:P003: External (DONE)

Transitive Dependencies (2 total):
  - P002: Infrastructure
  - tradeflow:P003: External

Projects Depending On This:
  - P004: Feature A (IN_PROGRESS)
  - P005: Feature B (PLANNING)
```

**Migration steps:**
1. Use `plan deps <project>` for ad-hoc queries
2. Use `plan graph-report` to find cycles before they cause problems
3. Use `plan blocked` to find what's preventing progress

**Example: Find Critical Blockers**
```python
from planner import PlanParser, DependencyGraph

files = PlanParser.parse_directory(Path("plan/"))
projects = {pf.entity.id: pf.entity 
            for pf in files.values() if hasattr(pf, 'entity')}

graph = DependencyGraph(projects)

# Find projects blocking many others
for project_id in projects:
    impact = graph.impact_analysis(project_id)
    if impact['directly_blocks'] > 2:
        print(f"{project_id} blocks {impact['directly_blocks']} projects")
```

### Pattern 4: Cross-Repo References

**Before:** String syntax, no validation
```yaml
depends:
  - ltools:L001
  - ldeps:D005
```

**After:** Validated with warnings
```bash
plan validate plan/
# ⚠ P001: depends reference ltools:L001 is external (allowed, not validated)
```

**Migration steps:**
1. Existing `repo:ID` syntax is fully supported
2. Cross-repo refs are allowed but not validated locally
3. In aggregated multi-repo setup, graph resolver will resolve them

### Pattern 5: Custom Priority Drivers

**Before:** Documentation only
```markdown
# plan/PRIORITY_DRIVERS.md
## Custom Drivers
| Driver | Weight | Definition |
| regulatory_compliance | +2.0 | Blocks due to compliance |
```

**After:** Programmatically used
```python
from planner import PriorityEngine

custom = {
    "regulatory_compliance": 2.0,
    "backtest_validation": 1.0,
}

engine = PriorityEngine(custom_drivers=custom)
score = engine.compute_score(["regulatory_compliance"])  # 2.0
```

**Migration steps:**
1. Define custom drivers as Python dict
2. Pass to `PriorityEngine(custom_drivers=...)`
3. Use in `priority_drivers` list in projects
4. Run validation to ensure driver names match

## Common Workflows

### Daily: Check What's Blocking Me

**Old way:**
```bash
# Manually read files, trace dependencies, look for BLOCKED status
grep -r "status: BLOCKED" plan/projects/
grep -r "depends:" plan/projects/P999.md
# Manual cross-reference
```

**New way:**
```bash
plan blocked plan/
# → Shows all blocked projects + their direct blockers

# Then drill down
plan deps P001 plan/
# → Shows what unblocks when P001 completes
```

### Weekly: Update Status & Priorities

**Old way:**
```bash
# Edit P001.md manually
# Update priority field
# Update status field
# Remember to update CHANGELOG.md
```

**New way:**
```bash
# Python script or manual edit, then validate
plan validate plan/  # Catches mismatches

# Identify priority mismatches
plan priority plan/ | grep "✗"
# → Fix any marked as mismatches
```

### Planning: Find Critical Path

**Old way:**
```bash
# Manually trace dependency chains
# Risk of circular references, incomplete analysis
```

**New way:**
```bash
# Automatic cycle detection + ordering
plan graph-report plan/
# → Shows any cycles immediately
# → Shows execution order (dependencies first)
# → Shows root/leaf projects (start/end points)
```

### Integration: CI/CD Validation

**Old way:**
```bash
#!/bin/bash
# In .github/workflows/validate.yml
./tools/validate.sh plan/ || exit 1
```

**New way:**
```bash
#!/bin/bash
# More comprehensive checks
PYTHONPATH=src python3 -m planner.cli validate plan/ || exit 1
PYTHONPATH=src python3 -m planner.cli graph-report plan/ | grep -q "Cycles: No" || exit 1
```

**Python-based approach:**
```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from planner import PlanParser, SchemaValidator, DependencyGraph, PriorityEngine

plan_dir = Path("plan/")
files = PlanParser.parse_directory(plan_dir)

# Extract entities
entities = {}
for pf in files.values():
    if hasattr(pf, 'entity'):
        entities[pf.entity.id] = pf.entity

# Validate schema
validator = SchemaValidator()
if not validator.validate_entity_all(entities.values()):
    print(f"❌ Schema validation failed")
    sys.exit(1)

# Validate relationships
if not validator.validate_relationships(entities):
    print(f"❌ Relationship validation failed")
    sys.exit(1)

# Check for cycles
graph = DependencyGraph({k: v for k, v in entities.items() if v.__class__.__name__ == 'Project'})
if graph.has_cycles():
    print(f"❌ Dependency cycles detected: {graph.find_cycles()}")
    sys.exit(1)

# Check priority mismatches
engine = PriorityEngine()
mismatches = []
for pid, project in entities.items():
    if project.__class__.__name__ == 'Project':
        analysis = engine.analyze_project(project)
        if not analysis['match']:
            mismatches.append(f"{pid}: {analysis['declared_priority']} → {analysis['computed_priority']}")

if mismatches:
    print(f"⚠️  Priority mismatches (fix before merge):")
    for m in mismatches:
        print(f"  - {m}")
    sys.exit(1)

print("✅ All validations passed")
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'planner'"

**Cause:** PYTHONPATH not set or wrong working directory

**Fix:**
```bash
# Option 1: Set PYTHONPATH
export PYTHONPATH="/path/to/lplan/src:${PYTHONPATH}"
plan validate plan/

# Option 2: Run from repo root
cd /path/to/lplan
PYTHONPATH=src python3 -m planner.cli validate plan/

# Option 3: Create alias
alias plan="PYTHONPATH=/path/to/lplan/src python3 -m planner.cli"
```

### Issue: "Referenced project P002 not found"

**Cause:** Project P002 doesn't exist, or dependency is in a different repo

**Fix:**
```bash
# Check if P002 exists
find plan/ -name "*P002*"

# If it's cross-repo (ltools:P001), that's OK - external refs are allowed
# If it's local, create the project or fix the reference

plan validate plan/  # Will show exact error
```

### Issue: Priority mismatch "computed=HIGH but declared=MEDIUM"

**Cause:** `priority_drivers` score doesn't match declared `priority`

**Fix:**
```bash
plan priority plan/  # Show the mismatch

# Option 1: Update priority to match computed
# Edit file and change: priority: MEDIUM → priority: HIGH

# Option 2: Add drivers to match declared priority
# If you want to keep MEDIUM, add drivers that score < 1.0

# Option 3: Add note in Log section explaining mismatch
# "2026-08-20 — Priority MEDIUM kept despite HIGH strategic value (blocked on P001)"
```

### Issue: "Graph has cycles"

**Cause:** Circular dependency detected (A depends on B, B depends on A)

**Fix:**
```bash
plan graph-report plan/
# Shows: Cycles detected (1):
#   P001 → P002 → P001

# Break the cycle by:
# 1. Check if dependency is really needed
# 2. Move dependency up to common ancestor
# 3. Create intermediate project to order phases
```

### Issue: CLI commands slow or hanging

**Cause:** Large plan directory or network issues with cross-repo resolution

**Fix:**
```bash
# Run with subset first
plan validate plan/projects/  # Just one subdirectory

# Or add debugging
python3 -c "
import sys; sys.path.insert(0, 'src')
from planner import PlanParser
from pathlib import Path
import time

start = time.time()
files = PlanParser.parse_directory(Path('plan/'))
print(f'Parse time: {time.time() - start:.2f}s')
print(f'Files: {len(files)}')
"
```

## Rollback Plan

If you need to revert to shell-based validation:

1. **Keep both running in parallel** (recommended approach):
   ```bash
   ./tools/validate.sh plan/        # Old validation
   plan validate plan/              # New validation
   # Both must pass during transition
   ```

2. **Git history is preserved**:
   ```bash
   git log --oneline -- tools/
   # Old scripts still available for reference
   ```

3. **Scripts remain unchanged**:
   - `plan/` directory format is identical
   - `schema/` documentation still valid
   - `templates/` still work

## Transition Timeline

### Week 1: Setup & Familiarization
- [ ] Install Python dependencies
- [ ] Run tests: `pytest tests/`
- [ ] Run CLI commands on existing plan
- [ ] Read IMPLEMENTATION.md for architecture

### Week 2: Validation & Priority Audit
- [ ] Run `plan validate` on plan, fix any errors
- [ ] Run `plan priority`, identify and fix mismatches
- [ ] Document any custom drivers needed
- [ ] Update CI to use new validator

### Week 3: Dependency Analysis
- [ ] Run `plan graph-report`, verify no cycles
- [ ] Use `plan deps <project>` for ad-hoc queries
- [ ] Map out critical path
- [ ] Document blockers and impact

### Week 4: Integration & Cleanup
- [ ] Update team scripts to use new CLI
- [ ] Update CI/CD pipelines
- [ ] Archive shell scripts (keep for reference)
- [ ] Add Python API usage to team docs

## FAQ

**Q: Do I have to use the Python engine?**  
A: No. The schema and file format remain the same. Shell scripts still work. The Python engine is optional but recommended for validation and analysis.

**Q: Can I use both in parallel?**  
A: Yes. Run both validators during transition to catch differences.

**Q: What if I have custom drivers?**  
A: Define them as Python dict and pass to `PriorityEngine(custom_drivers={...})`. Document in project README.

**Q: Does this work with monorepos/multi-repos?**  
A: Yes. Cross-repo refs (`ltools:P001`) are supported. Graph analyzer handles external nodes.

**Q: Can I extend the validator?**  
A: Yes. Subclass `SchemaValidator` and override validation methods. Full source available.

**Q: Is there a GUI?**  
A: Not yet. CLI is the current interface. Visualization tools are Tier 3.

**Q: How do I generate reports?**  
A: Use Python API to extract data, then generate reports:
   ```python
   report = graph.get_report()
   # Use pandas/matplotlib to create visualizations
   ```

## Support & Issues

- **Questions:** Check IMPLEMENTATION.md and code docstrings
- **Bug reports:** Include output of `plan validate` and `plan graph-report`
- **Feature requests:** File issue with use case and expected output
- **Performance:** Profile with `cProfile` and share results

---

**Ready to migrate?** Start with: `plan validate plan/`
