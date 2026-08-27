---
id: P010
title: Plan Health Dashboard
status: PLANNING
priority: HIGH
priority_drivers:
  - team_engagement
  - strategic_edge
created: 2026-08-27
updated: 2026-08-27
description: A live, hierarchy-aware status/progress view that shows the whole plan (Thesis→MasterPlan→Project→Design→Action, plus Concepts) at a glance, with rollups and "needs attention" surfacing — replacing INDEX.md's role as the de facto status view.
depends:
  - P004
  - P007
external_dependencies: []
enables: []
parent_master_plan:
  - M001
stakeholder: Engineering Leadership
---

## Goal

INDEX.md is the closest thing lplan has to a comprehensive status view, but it's a generated markdown snapshot: it lists every entity flat-per-type, requires an explicit regenerate to stay current, and shows no rollups (a Master Plan's page doesn't say "3/5 projects done"; a Project's page doesn't say "2/6 design tasks done"). Two web views exist that could have filled this gap but don't:

- **Items view** (`/api/status`, `status.js`): a flat, filterable/sortable table of all 6 entity types. Good for finding one entity; gives no aggregate picture.
- **Analytics dashboard** (`/api/analytics`, `analytics.js`): computes real rollups (fan-in/out, bottlenecks, capacity, impact) — but only over `Project` entities. Theses, Master Plans, Concepts, Designs, and Actions are invisible to it.

Neither answers "where do we actually stand, right now, across the whole hierarchy" in one place. This project builds that view: a live dashboard, always current (no regenerate step), that rolls progress up the hierarchy and actively surfaces what needs attention rather than requiring the reader to notice it (stale IN_PROGRESS entities, BLOCKED items, dangling references).

This is not a rewrite of Items view or Analytics — both stay as-is and remain useful for their own purposes (Items = find-one-entity; Analytics = project dependency mechanics). This is a new, third view.

## Scope

**In scope:**
- Hierarchy-wide rollups: per Master Plan (% of child projects done), per Project (% of child design/action tasks done), overall plan totals by status across all 6 entity types.
- "Needs attention" panel: BLOCKED entities and what blocks them (already computable via the dependency graph); IN_PROGRESS entities with no Log update in N days (stale-work detection — A015 sitting untouched since 2026-08-24 is the motivating real example); dangling references (already detected by the existing `plan check-refs` CLI command — as of this writing it flags A008/A011/A015 as orphaned and P009 as unused, real live examples to dogfood against).
- Thesis/Concept health strip: HELD/QUESTIONING/ABANDONED counts for Theses, STABLE/DRAFT/DEPRECATED counts for Concepts.
- New "Status" (or "Overview") tab in the web UI nav, alongside Tree/Items/Analytics.
- Clicking any rollup row drills into the existing entity view (reuse Items view's row-click navigation pattern).

**Out of scope (explicitly not this project):**
- Replacing or modifying Items view or the existing Analytics dashboard's Project-only metrics.
- Historical/time-series tracking (progress over time, trend lines) — CHANGELOG.md is the audit trail today; a time-series view is a plausible future project, not this one.
- Auto-fixing anything the "needs attention" panel surfaces (dangling refs, stale entities) — this is visibility only, not a remediation tool.
- Removing INDEX.md — it stays as the git-diffable, portable snapshot; this project addresses "I want to see current state without a repo checkout / without remembering to regenerate," not "INDEX.md should stop existing."

## Linked

- **Designs**: D004 (Plan Health Dashboard Architecture)
- **Actions**: A020, A021, A022, A023

## Tasks

### Phase 1: Design
- [ ] Write D004 covering rollup algorithm, staleness threshold, API shape, and UI layout

### Phase 2: Backend
- [ ] New rollup-aware endpoint (extends or sits alongside `/api/status`)
- [ ] Staleness detection (IN_PROGRESS + Log-age heuristic)
- [ ] Reuse `check-refs` logic for dangling-reference surfacing

### Phase 3: Frontend
- [ ] New `overview.js` module + nav tab
- [ ] Hierarchy rollup rendering (progress bars per Master Plan / Project)
- [ ] "Needs attention" panel

### Phase 4: Dogfood
- [ ] Validate against lplan's own `plan/` — confirm A015 shows as stale, P009 shows as the perpetual-catch-all edge case it is, and the A008/A011/A015 orphan refs surface correctly

## Log

2026-08-27 — Project created at user request: planned, not started. Scoped after reviewing existing Items view (flat table, no rollups) and Analytics dashboard (rollups, but Project-only) to confirm this is a real gap and not a duplicate of either.
