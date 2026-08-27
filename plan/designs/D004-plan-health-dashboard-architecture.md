---
id: D004
title: Plan Health Dashboard Architecture
status: DONE
project: P010
created: 2026-08-27
updated: 2026-08-27
doc_link: ""
---

## What

The data model and API shape for a hierarchy-wide rollup view, plus the algorithm for two specific "needs attention" signals: staleness and dangling references. Out of scope: the visual/CSS design of the dashboard itself (left to implementation) and any remediation tooling (this only surfaces, never fixes).

## Why

Building a fourth full entity-parsing pass felt wasteful — `/api/status` already parses every entity type and every existing view (`analytics.py`'s metrics module, `check-refs`) already implements pieces of what's needed. The chosen approach reuses those rather than reimplementing:

- Reuse `PlanParser.parse_directory` + the same six-way `isinstance` dispatch already in `/api/status` for the entity inventory.
- Reuse `DependencyGraph` (already built from Projects) for blocking/blocked-by relationships — no new dependency-resolution code.
- Reuse the reference-checking logic behind `plan check-refs` for dangling refs, rather than writing a second implementation of "does this ID exist."

Alternative considered: extend `/api/analytics` to cover all 6 entity types instead of adding a new endpoint. Rejected — `/api/analytics`'s metrics (fan-in/out, criticality, bottleneck chains) are specifically dependency-graph concepts that only make sense for Projects; forcing Theses/Concepts through the same shape would mean mostly-null fields. A separate endpoint with its own shape is more honest than overloading one.

## How

**Rollup algorithm** (bottom-up):
1. For each Project: `pct_done = count(child Designs/Actions with status DONE) / count(all child Designs/Actions)`. A Project with no children rolls up from its own status only (DONE=100%, else 0%).
2. For each Master Plan: `pct_done = count(child Projects with status DONE) / count(all child Projects via parent_master_plan)`. A Master Plan with no Projects yet shows 0% with an explicit "no projects yet" flag, not a misleading 100%-of-zero.
3. Overall: totals by status, grouped by entity type, computed directly from the full parsed set (no rollup needed, just counting).

**Staleness detection**: an entity is "stale" if `status == IN_PROGRESS` and `updated` (or the most recent `## Log` entry, whichever is later) is more than `N` days before now. Default `N = 3`, matching the gap that let A015 and FOCUS.md itself drift unnoticed. Configurable via a query param, not hardcoded — different plans move at different speeds.

**Dangling references**: shell out to (or import directly from) the same code path `plan check-refs` uses, and fold its "Orphaned Actions" / "Unused Projects" output into the needs-attention payload rather than requiring a separate CLI invocation.

## Where

**Architectural placement**: New Flask route in `server.py`, e.g. `/api/status-overview`, sitting next to `/api/status` and `/api/analytics` — not replacing either. New frontend module `overview.js` following the existing pattern in `analytics.js`/`status.js` (a class with `init()`/`load()`/`render()`), wired into `dispatcher.js` and `nav.js` the same way Items and Analytics are.

**Data ownership**: All data is derived, computed fresh on each request from the parsed `plan/` directory — nothing is cached or persisted server-side. Matches the existing `/api/status` and `/api/analytics` pattern (both re-parse on every call); no new state-lifetime concerns introduced.

**Initialization & lifecycle**: No new lifecycle — the endpoint is stateless per-request like its siblings.

## Constraints

- Must not modify `/api/status` or `/api/analytics` response shapes (Items view and Analytics dashboard depend on them as-is).
- Must handle an empty or partially-populated plan (no Master Plans yet, a Project with zero children) without divide-by-zero or misleading 100% figures.
- Rollup computation must stay fast enough for interactive use on lplan's own plan/ (31 entities today) — no specific budget set, but if a naive implementation is noticeably slow even at this size, that's a signal to revisit before shipping, not after.

## Migration

No stored/persisted data involved, so no migration path needed. Purely additive: a new route, a new frontend module, a new nav tab. Existing views and INDEX.md generation are untouched.

## Testability

The rollup and staleness functions should be pure (plan data in, rollup dict out) so they're unit-testable without spinning up Flask — same pattern as `metrics.py`/`impact.py`/`bottleneck.py`, which are already tested in isolation from `server.py`.

## Key Decisions

- **Decision**: New endpoint (`/api/status-overview`) rather than extending `/api/analytics` — keeps Project-specific dependency-graph metrics and hierarchy-wide rollups from being forced into one shape (see Why).
- **Decision**: Staleness and dangling-refs are surfaced, not auto-fixed — this project is a visibility tool; remediation (if wanted) is a separate future project so scope doesn't creep from "show me" to "fix it."

## Open Questions

- Should the default staleness threshold (3 days) be a plan-level config value (e.g. in a future `plan/config.yml`) rather than a query param default? Deferred until there's a second config-like setting to justify adding a config file at all.
- Should Concepts/Theses roll up into anything, or just show flat status counts? Current lean: flat counts only — they don't have children in the hierarchy sense, so a "rollup" would be synthetic.

## Related

- Project: P010
- Full doc: (none yet)
- Related: existing `/api/status` (Items view data source), `/api/analytics` (Project-only rollups), `plan check-refs` (dangling-reference detection), INDEX.md generation (`index_gen.py` — same six-entity-type grouping, different medium)

## Log

2026-08-27 — Implemented as designed: `status_overview.py` holds the pure rollup/staleness/dangling-ref functions, `/api/status-overview` in server.py is the thin Flask wrapper, `overview.js` is the frontend consumer. No deviations from the plan below.
2026-08-27 — Design created alongside P010, scoped to reuse existing parsing/graph/check-refs code rather than reimplement.
