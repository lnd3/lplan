# Documentation Index

Quick navigation for all Planner Framework documentation.

## Start Here

### 🚀 New Users
1. **[README.md](README.md)** — Overview of the framework
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Essential commands (bookmark this!)
3. **[QUICK_START](#quick-start-tldr)** — 5-minute setup (below)

### 📚 Migrating from Shell Scripts
1. **[MIGRATION.md](MIGRATION.md)** — Complete migration guide
   - Installation & setup
   - Common patterns and how they changed
   - Workflow examples
   - Troubleshooting common issues
   - 4-week transition timeline

### 🔧 Troubleshooting & Debugging
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Deep dive into issues
   - Installation problems
   - Validation errors
   - Priority scoring issues
   - Dependency graph problems
   - Debugging techniques
   - Performance optimization

### 🏗️ Building on the Framework
1. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** — Architecture & design
   - Component overview
   - Data models
   - Priority engine algorithm
   - Dependency graph analysis
   - Extension points
2. **[tests/](tests/)** — Test examples and usage patterns

---

## By Use Case

### "How do I check X?"

| Question | Answer |
|----------|--------|
| **Is my plan valid?** | `plan validate ./plan` — See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#validate-plan) |
| **What are project priorities?** | `plan priority ./plan` — See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#analyze-priorities) |
| **What depends on P001?** | `plan deps P001 ./plan` — See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#show-project-dependencies) |
| **What's blocking progress?** | `plan blocked ./plan` — See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#list-blocked-projects) |
| **Do I have circular dependencies?** | `plan graph-report ./plan` — See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#dependency-graph-report) |

### "How do I fix X?"

| Issue | Solution |
|-------|----------|
| **Priority mismatch** | [MIGRATION.md § Pattern 2](MIGRATION.md#pattern-2-priority-scoring) or [TROUBLESHOOTING.md § Priority mismatch](TROUBLESHOOTING.md#priority-mismatch-computed_highdeclared_medium) |
| **Broken dependency ref** | [TROUBLESHOOTING.md § Referenced project not found](TROUBLESHOOTING.md#referenced-project-p002-not-found) |
| **Circular dependencies** | [TROUBLESHOOTING.md § Cycles detected](TROUBLESHOOTING.md#cycles-detected) |
| **Slow validation** | [TROUBLESHOOTING.md § Performance](TROUBLESHOOTING.md#slow-validation-on-large-plans) |
| **Installation failing** | [TROUBLESHOOTING.md § Installation Issues](TROUBLESHOOTING.md#installation-issues) |

### "How do I set up X?"

| Task | Instructions |
|------|--------------|
| **Install Python engine** | [QUICK_REFERENCE.md § Installation](QUICK_REFERENCE.md#installation) |
| **Migrate from shell scripts** | [MIGRATION.md § Installation & Setup](MIGRATION.md#installation--setup) |
| **Integrate with CI/CD** | [QUICK_REFERENCE.md § CI/CD](QUICK_REFERENCE.md#cicd-githubworkflowsvalidate-yml) or [MIGRATION.md § Integration](MIGRATION.md#integration-cicd-validation) |
| **Use custom drivers** | [MIGRATION.md § Pattern 5](MIGRATION.md#pattern-5-custom-priority-drivers) or [IMPLEMENTATION.md](IMPLEMENTATION.md#priority-scoring-engine) |
| **Write Python scripts** | [QUICK_REFERENCE.md § Python API](QUICK_REFERENCE.md#python-api) or [IMPLEMENTATION.md](IMPLEMENTATION.md) |

---

## Documentation Map

```
README.md
  ↓
  ├─ For quick start → QUICK_REFERENCE.md
  ├─ For migration → MIGRATION.md
  ├─ For problems → TROUBLESHOOTING.md
  └─ For architecture → IMPLEMENTATION.md
                          ↓
                        tests/ (examples)
```

## Document Descriptions

### [README.md](README.md)
- **Purpose:** Framework overview and entry point
- **Audience:** Everyone
- **Length:** ~150 lines
- **Update:** Just refreshed to highlight Python engine

### [QUICK_REFERENCE.md](QUICK_REFERENCE.md) ⭐
- **Purpose:** Quick lookup for commands and patterns
- **Audience:** Daily users, developers
- **Length:** ~240 lines
- **Print-friendly:** Yes (fits on 3 pages)
- **Bookmark this!**

### [MIGRATION.md](MIGRATION.md) ⭐
- **Purpose:** Guide from shell scripts to Python engine
- **Audience:** Users upgrading from old approach
- **Length:** ~500 lines
- **Key sections:**
  - Pattern-by-pattern migration (5 patterns)
  - Before/after comparisons
  - Daily/weekly workflows
  - 4-week transition timeline
  - FAQ and troubleshooting

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md) ⭐
- **Purpose:** Issue diagnosis and resolution
- **Audience:** Users fixing problems
- **Length:** ~900 lines
- **Key sections:**
  - Installation issues
  - File parsing errors
  - Validation failures
  - Priority computation issues
  - Dependency graph problems
  - Debugging techniques

### [IMPLEMENTATION.md](IMPLEMENTATION.md)
- **Purpose:** Architecture and extension guide
- **Audience:** Developers, framework contributors
- **Length:** ~380 lines
- **Key sections:**
  - Component descriptions with code
  - Data models and validation
  - Priority scoring algorithm
  - Dependency graph analysis
  - Parser and CLI design

### [DOCS_INDEX.md](DOCS_INDEX.md) (This File)
- **Purpose:** Navigation hub
- **Audience:** Everyone
- **Length:** ~300 lines
- **Use:** When you're not sure where to look

---

## Quick Start (TL;DR)

### Installation (2 minutes)
```bash
pip install pyyaml click networkx pydantic python-dateutil
export PYTHONPATH="${PWD}/src"
```

### Validation (1 minute)
```bash
plan validate ./plan/
# Output: ✓ Validation passed (42 entities)
```

### Priority Analysis (1 minute)
```bash
plan priority ./plan/ | head -20
# Shows: Project priorities, scores, driver breakdown
```

### Dependency Analysis (2 minutes)
```bash
plan deps P001 ./plan/
plan blocked ./plan/
plan graph-report ./plan/
```

**Next:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more commands.

---

## File Organization

```
📄 Documentation (2,500+ lines)
├── README.md                  # Entry point
├── QUICK_REFERENCE.md        # Cheat sheet ⭐
├── MIGRATION.md              # Migration guide ⭐
├── TROUBLESHOOTING.md        # Issue resolution ⭐
├── IMPLEMENTATION.md         # Architecture guide
└── DOCS_INDEX.md            # This file

🐍 Python Engine (2,300+ lines)
├── src/planner/
│   ├── models.py            # Pydantic models
│   ├── parser.py            # File parser
│   ├── validator.py         # Schema validator
│   ├── priority.py          # Priority scoring
│   ├── graph.py             # Dependency analysis
│   └── cli.py               # CLI commands
└── tests/                   # 58 test cases

📋 Reference (Unchanged)
├── schema/                  # Formal specifications
├── templates/               # Boilerplate files
└── tools/                   # Legacy shell scripts
```

---

## Common Workflows

### Daily: Check Status
```bash
plan validate ./plan/              # Sanity check
plan blocked ./plan/               # See blockers
plan priority ./plan/ | grep "✗"   # Find mismatches
```

### Weekly: Update Progress
```bash
# Edit plan/projects/P*.md
# Update status, add to log

plan validate ./plan/              # Check for errors
plan priority ./plan/              # Update mismatches
```

### Planning: Find Critical Path
```bash
plan graph-report ./plan/          # Cycle detection, execution order
plan deps P001 ./plan/ > deps.txt  # Build dependency tree
```

### Integration: CI/CD Validation
```bash
PYTHONPATH=src python3 -m planner.cli validate ./plan/
```

See [MIGRATION.md](MIGRATION.md) for more workflow examples.

---

## Getting Help

1. **"How do I...?"** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. **"I'm migrating"** → [MIGRATION.md](MIGRATION.md)
3. **"Something's broken"** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **"How does this work?"** → [IMPLEMENTATION.md](IMPLEMENTATION.md)
5. **"Show me code"** → [tests/](tests/)

---

## Version & Status

- **Framework Version:** 0.1.0
- **Python Engine:** ✅ Production-ready (58/58 tests passing)
- **Documentation:** ✅ Complete and tested
- **Last Updated:** 2026-08-20

## Feedback & Issues

Questions? Issues? Check:
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues
2. [tests/](tests/) for usage examples
3. [IMPLEMENTATION.md](IMPLEMENTATION.md) for design details

---

**Start with:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [MIGRATION.md](MIGRATION.md)
