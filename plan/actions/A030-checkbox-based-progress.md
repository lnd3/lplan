---
id: A030
title: Checkbox-Based Progress for Project/Master Plan Rollups
status: DONE
design: D004
project: P010
created: 2026-08-30
updated: 2026-08-30
---

## Context

User's critique of the original rollup math: `pct_done` was computed from child Design/Action DONE-counts, but the child set grows as work gets discovered mid-flight (mostly upward), so that percentage drifts in ways that don't reflect real progress. Every project already has a `## Tasks` section with human-maintained `- [ ]`/`- [x]` checkboxes (per the template, independent of D008); those are the deliberate plan of record and should drive the percentage instead. User also confirmed this applies to Master Plans, which have the same Tasks/Phases checkbox structure (see M001's own rewrite).

## Tasks

- [x] New `parser.count_checkboxes()` — scans a file's whole raw body for `- [ ]`/`- [x]` regardless of section name, so it works for both the existing `## Tasks` convention and D008's `## Phases` convention without special-casing either
- [x] `status_overview._rollup_pct()`: shared logic for `project_rollup()`/`master_plan_rollup()` — prefers checkbox completion, falls back to child-entity-DONE-count when there are no checkboxes, falls back to entity status when there's neither
- [x] New `pct_source` field (`"checkboxes"` / `"children"` / `"status"`) plus `checkbox_done`/`checkbox_total` in the rollup payload, so the dashboard can show which signal actually drove the number instead of implying they're interchangeable
- [x] `overview.js`: rollup rows now show the fraction matching the actual `pct_source` (task count when checkbox-derived, child count when not), with a `(by children)` note when falling back
- [x] 4 new tests in `test_status_overview.py`: checkboxes win over disagreeing child counts, falls back to children when no checkboxes exist, falls back to status when neither exists, same checkbox-preference behavior for master plans
- [x] Verified live against a running `plan serve`: real numbers changed sensibly (P001 100%, P007 73%, P008 0%, P009 correctly falls back to "children" since its Tasks section is explicitly N/A)

## Real finding while dogfooding

Running this against lplan's own plan/ immediately surfaced a genuine data-quality issue: **P002 and P003 were both marked DONE with 0% checkbox completion** — all their Tasks checkboxes had been left unchecked despite the actual work being real and documented in their own Log entries (impact analysis, Gantt/burndown charts, analytics dashboard, etc.). Fixed both files' checkboxes to match reality, but conservatively — cross-checked each item against the codebase before checking it off, and left 2 of P003's 9 items unchecked ("Mermaid diagram generation," "Status propagation engine") since neither has any evidence of having been built. See P002/P003's own Log entries for detail.

This is the same class of problem A027 catches at the child-entity level (DONE parent, non-terminal children) but at the checkbox level instead (DONE entity, unchecked tasks) — worth considering as a future validator check, not implemented here.

## Log

2026-08-30 — Implemented, tested (118/118 total suite), and used to find + fix a real stale-checkbox issue in P002/P003. P010 stays DONE — enhancement, not a scope reopening.
