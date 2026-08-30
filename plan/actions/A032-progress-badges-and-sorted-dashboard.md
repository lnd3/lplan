---
id: A032
title: Tree View Progress Badges, Items View Label Rename, Status Dashboard Sort
status: DONE
design: D004
project: P010
created: 2026-08-30
updated: 2026-08-30
---

## Context

Three follow-on requests, all reusing A030's checkbox-based rollup math so the number agrees everywhere it's shown:
1. Tree view: small progress badge at the end of Project/Master Plan titles
2. Rename the "COMPLETION" column header to "PROGRESS" in the Items view (`status.js`) — the request said "Tree view" but Tree view has no such label to rename; Items view is where "COMPLETION" actually exists, from A031
3. The "🩺 Status" dashboard (P010's own `overview.js`): sort project/master-plan rollups by progress, least complete first — distinct from A031's Items-view sort, since this view still sorted by ID

**Interpretation note**: (2) and (3) both hinge on which view "Status view"/"Tree view" meant, given this repo has three plausibly-named views (Items view is literally the `StatusView` class; the toolbar button for `overview.js` is literally labeled "🩺 Status"). Went with the reading that makes all three requests non-redundant and internally consistent — flagged to the user in case the guess was wrong.

## Tasks

- [x] `server.py`'s `_build_hierarchy()`: `proj_node`/`mp_node` now carry a `completion` field, computed via `project_rollup()`/`master_plan_rollup()` (needed to thread full entity objects + `PlanFile`s through, which the lightweight tree-node dicts didn't previously keep)
- [x] `tree.js`: new `TreeView.progressBadge()`, small and muted (gray unless 100%, then green), placed right after the title in both the Projects tree and the Master Plans list
- [x] `status.js`: column header label for `completion` special-cased to render "PROGRESS" instead of the auto-generated "COMPLETION" (kept the underlying field name `completion` — only the displayed label changed, to avoid unnecessary churn)
- [x] `status_overview.py`: `project_rollups`/`master_plan_rollups` now sorted by `(pct_done, id)` ascending before being returned, instead of by `id` alone — `id` stays as a stable tiebreaker for equal-progress rows
- [x] New test: `compute_status_overview()`'s project rollups come back least-complete-first for three projects with deliberately different checkbox completion
- [x] Verified all three live via jsdom against a running `plan serve`: Tree view renders a `Progress` badge, Items view header reads "PROGRESS", Status dashboard project order is `P008, P007, P003, P001, ...` (0%, 73%, 78%, then the 100%s)

## Log

2026-08-30 — Implemented and verified live for all three (not just via curl/API). 119/119 tests pass (118 + 1 new sort-order test).
