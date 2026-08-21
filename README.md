# lplan — Structured Planning Framework

A generic, reusable planning system for organising projects, designs, and actions across software repositories. Designed to work as a git submodule.

## Core Idea

Plans scale by adding files, not by adding fields. Each concern gets its own flat, readable document:

| File | Purpose | Updated |
|------|---------|---------|
| `INDEX.md` | Dashboard — all projects, designs, actions at a glance | Auto-generated or manually maintained |
| `FOCUS.md` | Current active work, what's blocked, what's next | Rewritten each session |
| `CHANGELOG.md` | Append-only status change log | Appended on every status change |
| `REFLECTION.md` | Learnings, gotchas, patterns — accumulated project intuition | Appended as insights are discovered |
| `VALIDATION.md` | Validation workflow and common errors | Reference |
| `README.md` | This file — framework overview | Reference |
| `projects/` | High-level goals (P001, P002, …) | Edited directly |
| `designs/` | Architectural decisions (D001, D002, …) | Edited directly |
| `actions/` | Concrete task lists (A001, A002, …) | Edited directly |

---

## Quick Start

### 1. Install

```bash
# Core (required)
pip install pyyaml click networkx pydantic python-dateutil

# Web UI (optional)
pip install flask
```

### 2. Initialise a plan

```bash
# In your repo root (lplan as submodule at deps/lplan):
./deps/lplan/bin/plan init ./plan --name "MyProject"
```

Creates: `INDEX.md`, `FOCUS.md`, `CHANGELOG.md`, `REFLECTION.md`, `VALIDATION.md`, `README.md`, `projects/`, `designs/`, `actions/`

### 3. Validate before committing

```bash
./deps/lplan/bin/plan validate ./plan
```

### 4. Browse in the browser

```bash
./deps/lplan/bin/plan serve ./plan          # read-only
./deps/lplan/bin/plan serve ./plan --edit   # with editing
# Then open http://127.0.0.1:8000
```

---

## CLI Commands

### Daily workflow

```bash
plan validate ./plan                    # Validate before committing
plan generate-index ./plan              # Regenerate INDEX.md (auto-detects repo name)
plan priority ./plan                    # Check priority scores vs declared priority
plan blocked ./plan                     # List blocked projects and their blockers
```

### Analysis

```bash
plan deps P001 ./plan                   # Show what blocks P001 and what P001 blocks
plan graph-report ./plan                # Full dependency graph (cycles, roots, leaves)
plan stats ./plan                       # Aggregate counts and % done
plan timeline ./plan                    # Execution phases (what can run in parallel)
plan check-refs ./plan                  # Find broken links and orphaned entities
```

### Editing

```bash
plan log P001 "Started work" ./plan                  # Append to entity log
plan log P001 "Done" ./plan --status DONE            # Append + update status
plan update P001 ./plan --status IN_PROGRESS         # Update frontmatter field
plan update P001 ./plan --priority HIGH
```

### Web UI

```bash
plan serve ./plan                       # Start browser UI (read-only, port 8000)
plan serve ./plan --edit                # Enable file editing
plan serve ./plan --port 9000           # Custom port
plan stop ./plan                        # Stop running server (reads .plan-server.pid)
plan restart ./plan                     # Restart with same options
```

### Other

```bash
plan report ./plan -o report.html       # Generate HTML report (also available in web UI)
plan commit ./plan -m "Update P001"     # Validate + git commit in one step
plan watch ./plan                       # Watch for changes (Ctrl-C to stop)
plan init ./plan --name "Name"          # Initialise new plan directory
```

---

## Plan File Formats

### Project (`projects/P001-name.md`)

```yaml
---
id: P001
title: My Project
status: IN_PROGRESS
priority: HIGH
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-20
depends: [P002]
external_dependencies: []
enables: [P003]
---

## Goal
What this project achieves and why.

## Scope
- Included: A, B, C
- Not included: X, Y

## Tasks
### Phase 1
- [x] Done item
- [ ] Pending item

## Log
2026-08-20 — Project created.
```

### Design (`designs/D001-name.md`)

```yaml
---
id: D001
title: My Design
status: PLANNING
project: P001
created: 2026-08-20
updated: 2026-08-20
---
```

### Action (`actions/A001-name.md`)

```yaml
---
id: A001
title: My Action
status: IN_PROGRESS
priority: HIGH
priority_drivers:
  - enables_multiple
design: D001
project: P001
created: 2026-08-20
updated: 2026-08-20
depends: []
external_dependencies: []
---
```

---

## Status Values

`IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

## Priority Values

`HIGH` · `MEDIUM` · `LOW`

Priority is computed from `priority_drivers`. See `schema/priority-framework.md` for driver weights.

---

## FOCUS.md Workflow

`FOCUS.md` is rewritten (not appended) each session. It answers: *what is being worked on right now, what is blocked, and what comes next.* Keeping it current costs one minute per session and eliminates the "where were we?" reconstruction cost at session start.

## REFLECTION.md Workflow

`REFLECTION.md` is append-only, one entry per insight:

```
YYYY-MM-DD | CATEGORY | insight text
```

Categories: `GOTCHA` · `PATTERN` · `LEARNING` · `WARNING` · `DECISION`

Write an entry when something surprises you, when an assumption turns out to be wrong, or when a pattern generalises across multiple situations. This builds up project intuition that persists across context resets.

---

## Validation Requirement

Always validate before committing changes to `plan/`:

```bash
./deps/lplan/bin/plan validate ./plan
```

See `plan/VALIDATION.md` for common errors and fixes.

Optional pre-commit hook (`.git/hooks/pre-commit`):

```bash
#!/bin/bash
if git diff --cached --name-only | grep -q '^plan/'; then
    ./deps/lplan/bin/plan validate ./plan || exit 1
fi
```

---

## Adding as a Submodule

```bash
git submodule add https://github.com/lnd3/lplan deps/lplan
./deps/lplan/bin/plan init ./plan --name "MyProject"
```

Update lplan:

```bash
cd deps/lplan && git pull origin main && cd ..
git add deps/lplan && git commit -m "Update lplan"
```

---

## Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Command cheat sheet
- **[VALIDATION.md](VALIDATION.md)** — Validation workflow and common errors
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Issue resolution
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** — Architecture and extension points
- **[schema/](schema/)** — Formal specifications
