---
id: P009
title: External Maintenance
status: IN_PROGRESS
priority: LOW
priority_drivers:
  - critical_live_path_only
created: 2026-08-27
updated: 2026-08-27
description: Catch-all project for drive-by bug fixes and layout fixes landed by agents/humans whose active task was in another repo, not lplan's own plan. See WORKFLOW.md § "External Contribution Workflow (Drive-By Fixes)".
depends: []
external_dependencies: []
enables: []
---

## Goal

Give drive-by contributions to lplan's own source a place to attach without requiring up-front triage into a specific project. Every Action logged here is expected to already be `DONE` at creation — this project tracks completed fixes, not planned work.

## Scope

- In scope: bug fixes and layout/UX fixes made to lplan's own `src/`, `templates/`, or `schema/` by contributors not actively working from lplan's `plan/`.
- Not in scope: new capabilities, entity types, or behavior changes (those need a real project/design and the full WORKFLOW.md treatment, not a drive-by Action here).

## Linked

- **Projects**: none — actions here may later be re-filed into P001–P008 during a normal upkeep pass.
- **Designs**: none.
- **Actions**: A016, A017, A018, A019, A024

## Tasks

N/A — this project has no task list of its own. Its "tasks" are the Actions logged under it, each already complete.

## Log

2026-08-27 — Project created as part of fleshing out the drive-by contribution convention (WORKFLOW.md). No actions filed yet; status stays IN_PROGRESS indefinitely since it's an ongoing catch-all, not a project that reaches DONE.
2026-08-27 — Backfilled A016–A019: tree-view click/highlight/dedup fixes, root-badge coverage for all parentless items (including actions that previously vanished from the tree entirely), Save/Cancel button visibility, sidebar toggle glyphs, INDEX.md edit-disable, README-based repo name, and full thesis<->master_plan bidirectional display — all landed drive-by from superplan's context before this convention existed, filed retroactively at the user's request.
