---
id: A020
title: Backend rollup API (/api/status-overview)
status: DONE
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

Implements D004's rollup algorithm as a new Flask endpoint, reusing `PlanParser`, `DependencyGraph`, and the `check-refs` logic rather than reimplementing entity parsing or reference checking.

## Tasks

### Rollups
- [x] Bottom-up Project rollup: % of child Designs/Actions DONE
- [x] Bottom-up Master Plan rollup: % of child Projects DONE, with explicit "no projects yet" flag for empty master plans
- [x] Overall totals by status, grouped by entity type

### Needs-attention signals
- [x] Staleness: IN_PROGRESS + no Log/updated activity in N days (default 3, query-param configurable via `?stale_days=`)
- [x] Blocked entities + blocker list (reuse `DependencyGraph`)
- [x] Dangling references (reuse `check-refs` code path, not a shell-out)

### Route
- [x] New `/api/status-overview` route in `server.py`
- [x] Pure functions for rollup/staleness in new `src/planner/status_overview.py` (testable without Flask), matching `metrics.py`/`impact.py` pattern

## Log

2026-08-27 — Implemented `status_overview.py` (compute_status_overview + helpers) and wired `/api/status-overview` into server.py. Verified directly against lplan's own plan/ via a standalone script and via curl against a running `plan serve`: output matches `plan check-refs` exactly (A008/A011/A015 orphaned, P009 unused) and correctly flags A015/P007/M001 as stale. Existing 100-test suite still passes unchanged.
2026-08-27 — Action created, not started.
