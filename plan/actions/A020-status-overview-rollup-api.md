---
id: A020
title: Backend rollup API (/api/status-overview)
status: IDEA
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

Implements D004's rollup algorithm as a new Flask endpoint, reusing `PlanParser`, `DependencyGraph`, and the `check-refs` logic rather than reimplementing entity parsing or reference checking.

## Tasks

### Rollups
- [ ] Bottom-up Project rollup: % of child Designs/Actions DONE
- [ ] Bottom-up Master Plan rollup: % of child Projects DONE, with explicit "no projects yet" flag for empty master plans
- [ ] Overall totals by status, grouped by entity type

### Needs-attention signals
- [ ] Staleness: IN_PROGRESS + no Log/updated activity in N days (default 3, query-param configurable)
- [ ] Blocked entities + blocker list (reuse `DependencyGraph`)
- [ ] Dangling references (reuse `check-refs` code path, not a shell-out)

### Route
- [ ] New `/api/status-overview` route in `server.py`, response shape documented inline
- [ ] Pure functions for rollup/staleness (testable without Flask), matching `metrics.py`/`impact.py` pattern

## Log

2026-08-27 — Action created, not started.
