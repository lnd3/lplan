---
id: A031
title: Items View — Completion Column + Default Sort Least-Complete-First
status: DONE
design: D004
project: P010
created: 2026-08-30
updated: 2026-08-30
---

## Context

User request: sort projects in the Items view (`status.js`) by completion, least complete first. Reuses A030's checkbox-based rollup math directly rather than reimplementing it, so the number shown here always matches the Status Overview dashboard.

## Tasks

- [x] `/api/status` (server.py): each `master_plan`/`project` entity now carries `completion` (`pct_done`) and `completion_source`, computed via `status_overview.project_rollup()`/`master_plan_rollup()` — same function P010's dashboard uses, not a reimplementation
- [x] `status.js`: new "Completion" column (small progress bar + %, tooltip explaining the source when it's not checkbox-derived); other entity types (concept/thesis/design/action) show `—`, no fake 0%
- [x] Default `sortConfig` changed from `{column: 'id', direction: 'asc'}` to `{column: 'completion', direction: 'asc'}` — least complete first, as asked
- [x] `sortData()`: special-cased the completion column so entities with no completion measure sort to the end regardless of direction, instead of the generic null→`''` fallback silently treating "no measure" as "0% done"
- [x] Verified live via jsdom: filtered to Projects, confirmed real row order is P008 (0%) → P007 (73%) → P003 (78%) → the rest at 100%, and the column header shows the ascending sort arrow

## Log

2026-08-30 — Implemented and verified live (not just via curl). 118/118 tests pass (no regressions; no new Python tests added since this is thin server.py/status.js wiring around already-tested `status_overview` functions — verification was via jsdom DOM execution against a running server instead).
