---
id: D007
title: Analytics Architecture
status: DONE
project: P007
created: 2026-08-23
updated: 2026-08-30
doc_link: ""
---

## What

The architecture behind P007's analytics/reporting surface: project metrics (fan-in/out, depth, criticality), bottleneck detection, impact analysis, timeline phase computation, and three SVG visualizations (Gantt, burndown, dependency graph). Written retroactively (2026-08-30) — the code was built across several sessions without a design doc ever actually landing, even though P007 and A015 both referenced this ID from the start. `plan check-refs` had been flagging A015 as orphaned as a result; this closes that gap with an accurate record instead of a placeholder.

## Why

One module per concern, each independently testable, rather than one large "analytics" module: `metrics.py` (fan-in/out/depth/criticality), `impact.py` (what unblocks when a project completes), `bottleneck.py` (blocking chains, cycles, high fan-out — built on top of `metrics.py`), `capacity.py` (parallelization/timeline), `gantt.py` / `burndown.py` (SVG chart generation), and `report.py` (assembles everything, including its own SVG dependency-graph renderer, into a static HTML report). This mirrors the separation-of-concerns pattern already noted as working well in `plan/REFLECTION.md`.

## How

- `/api/analytics` (server.py) computes metrics + impact + bottlenecks + capacity fresh on every request (no caching), same pattern as `/api/status-overview`.
- `/api/chart/gantt` and `/api/chart/burndown` return standalone SVG strings; `analytics.js`'s `renderAnalyticsDashboard()` fetches both and appends them into the Analytics tab — this is the live, interactive dashboard.
- `report.py`'s `_generate_dependency_graph_svg()` independently implements a phase-based dependency graph (phase columns on X, projects within a phase stacked on Y, status-colored nodes, arrowed edges) for the static HTML report (`plan report` / `/report`) — this is a *second*, separate SVG renderer from the Gantt/burndown ones, not shared code.

## Where

**Architectural placement**: `src/planner/{metrics,impact,bottleneck,capacity,gantt,burndown,report}.py`, wired into `server.py`'s Flask routes and `cli.py`'s `report` command. No shared base class between the two SVG-generation code paths (dashboard charts vs. static-report dependency graph) — they evolved independently and still are independent.

**Data ownership**: Stateless — every route/command re-parses `plan/` and recomputes from scratch. No persisted analytics state anywhere (relevant to the "Historical tracking and trends" task in P007's Phase 3, which is unstarted specifically because there's nowhere to persist a time series yet).

## Constraints

- Dependency-graph SVG (`report.py`) is static-report-only — it is **not** currently wired into the live Analytics dashboard. Someone opening the "📊 Analytics" tab sees Gantt + burndown, not a dependency graph; someone running `plan report` sees the dependency graph but not an interactive one. This is the gap A015 is still open against.
- The static-report dependency graph has no hover tooltips or click-to-navigate — it's plain SVG in a static HTML file, so neither is meaningful there. If the graph gets wired into the live dashboard instead, interactivity becomes possible using the same click→`EntityViewer.show()` pattern P010's `overview.js` already uses.

## Migration

N/A — additive, no prior version of this architecture existed to migrate from.

## Testability

`metrics.py`/`impact.py`/`bottleneck.py`/`capacity.py` are pure functions over `projects`/`graph`, already unit-tested independently of Flask (see `tests/test_stats.py`, `tests/test_graph.py`). `report.py`'s `_generate_dependency_graph_svg()` has no dedicated test — `tests/test_report.py` exercises `generate_html_report()` end-to-end but doesn't assert anything about the dependency-graph SVG specifically (see A015).

## Key Decisions

- **Decision**: Two independent SVG code paths (dashboard charts vs. static-report dependency graph) instead of one shared renderer. Never revisited — this design doc is the first time it's been written down, so treat this as documenting what happened rather than a considered tradeoff.

## Open Questions

- Should the dependency-graph SVG move into the live Analytics dashboard (making A015's remaining scope live-dashboard integration + interactivity), or is the static-report version sufficient and A015's remaining tasks should be re-scoped/dropped? Not decided — see A015's Log.

## Related

- Project: P007
- Related: A014 (metrics computation), A015 (dependency graph visualization — the specific piece this design doc's "Open Questions" concerns), P010 (Plan Health Dashboard — a related-in-spirit dashboard, but rollups/health, not dependency mechanics; no code shared with this design)

## Log

2026-08-30 — Written retroactively to close a `check-refs`-flagged orphan (A015's `design: D007` never resolved) and to accurately record what P007's analytics work actually built, discovered while aligning P007 with current state at user request.
