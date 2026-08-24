# lplan — Structured Planning Framework

A generic, reusable planning system for organising decisions across software
repositories. Designed to work as a git submodule.

> *This document is not philosophy for its own sake. It is a reminder of what
> planning is for: to make decisions better, faster, and with less waste — in
> service of an existence that is finite and will not be repeated.
> That is sufficient reason to plan well.*

---

## Core Idea

Every plan is downstream of a decision to plan.
Every decision is downstream of an existence that decided to show up.

The framework makes that chain explicit. Six layers, each answering a different
question — moving from unconstrained belief to concrete action:

| Layer | Prefix | Question answered |
|-------|--------|-------------------|
| `ORIGIN.md` | — | Why plan at all? |
| `AXIOMS.md` | — | What constraints apply to all decisions? |
| `theses/` | T | What do I believe about the world? *(falsifiable)* |
| `master_plans/` | M | When are conditions right to act on it? |
| `projects/` | P | What will we build? |
| `designs/` | D | How will we build it? |
| `actions/` | A | What specifically needs to be done? |

Plans scale by adding files, not by adding fields. Each concern gets its own
flat, readable document.

### Session documents

| File | Purpose | Updated |
|------|---------|---------|
| `INDEX.md` | Dashboard — full hierarchy at a glance | Auto-generated or hand-maintained |
| `FOCUS.md` | Current work, blockers, what's next | Rewritten each session |
| `CHANGELOG.md` | Append-only status change log | On every status change |
| `REFLECTION.md` | Learnings, gotchas, patterns | Appended as insights arrive |
| `VALIDATION.md` | Validation workflow and common errors | Reference |

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

Creates: `ORIGIN.md`, `AXIOMS.md`, `INDEX.md`, `FOCUS.md`, `CHANGELOG.md`,
`REFLECTION.md`, `VALIDATION.md`, `theses/`, `master_plans/`, `projects/`,
`designs/`, `actions/`

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
plan report ./plan -o report.html       # Generate HTML report
plan commit ./plan -m "Update P001"     # Validate + git commit in one step
plan watch ./plan                       # Watch for changes (Ctrl-C to stop)
plan init ./plan --name "Name"          # Initialise new plan directory
```

---

## Plan File Formats

### Thesis (`theses/T001-name.md`)

Unconstrained belief about the world. Has a falsification condition —
without one, it is a preference, not a thesis.

```yaml
---
id: T001
title: One sentence — a falsifiable belief about how the world works
status: HELD
conviction: 8
created: 2026-08-20
updated: 2026-08-20
---

## The Belief
State the conviction plainly. Write it so someone could argue against it.

## Why This Could Be True
Two or three grounding observations. Brief — not a proof.

## What Would Change My Mind
Explicit falsification criteria. What evidence moves this to QUESTIONING or ABANDONED?

## Entropic Constraints
- **Decay mechanism**: what force works against this thesis?
- **Horizon**: rough timeframe before the edge compresses
- **Early warning signs**: observable signals of compression
- **What comes after**: successor thesis, or domain becomes unplayable?

## Master Plans Seeded by This
- [[M001]] — activated when [condition]

## Log
2026-08-20 — Thesis formed.
```

### Master Plan (`master_plans/M001-name.md`)

Constrained possibility: a thesis made actionable by current market,
technology, and competitive conditions. Answers *when*, not *how*.

```yaml
---
id: M001
title: Strategic direction in one sentence
status: IN_PROGRESS
stakeholder: Name
vision: What changes in the world when this succeeds?
priority: HIGH
parent_thesis: [T001, T002]
goals:
  - Observable external outcome 1
  - Observable external outcome 2
created: 2026-08-20
updated: 2026-08-20
---

## Goal
WHY this matters — framed outward. What market or technology condition makes
this worth pursuing now? Do not describe the solution.

## Market Window
- **Opens**: what makes this timely now?
- **Closes**: what compresses the opportunity?
- **Peak value**: when is return highest?

## External Forces
Market trends, competition, technology, regulatory context.

## Success Looks Like
Externally observable outcome — not internal deliverables.

## Linked
- **Projects**: P001, P002
- **Other Master Plans**: M002

## Log
2026-08-20 — Master plan created.
```

### Project (`projects/P001-name.md`)

```yaml
---
id: P001
title: My Project
status: IN_PROGRESS
priority: HIGH
priority_drivers:
  - strategic_edge
parent_master_plan: [M001]
created: 2026-08-20
updated: 2026-08-20
depends: [P002]
---

## Goal
## Scope
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
---
```

---

## Status Values

Standard: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

Thesis-specific: `HELD` · `QUESTIONING` · `ABANDONED`

## Priority Values

`HIGH` · `MEDIUM` · `LOW`

Priority is computed from `priority_drivers`. See `schema/priority-framework.md`.

---

## FOCUS.md Workflow

`FOCUS.md` is rewritten (not appended) each session. It answers: *what is being
worked on right now, what is blocked, and what comes next.* Keeping it current
costs one minute per session and eliminates the "where were we?" reconstruction
cost at session start.

## REFLECTION.md Workflow

`REFLECTION.md` is append-only, one entry per insight:

```
YYYY-MM-DD | CATEGORY | insight text
```

Categories: `GOTCHA` · `PATTERN` · `LEARNING` · `WARNING` · `DECISION`

Write an entry when something surprises you, when an assumption turns out to
be wrong, or when a pattern generalises across multiple situations.

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
