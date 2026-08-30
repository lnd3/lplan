---
id: P007
title: Analytics & Reporting Dashboard
status: IN_PROGRESS
priority: MEDIUM
priority_drivers:
  - team_engagement
  - strategic_edge
created: 2026-08-23
updated: 2026-08-30
description: Build analytics dashboard with project metrics, dependency graphs, burndown charts, and timeline visualization.
depends:
  - P002
  - P004
external_dependencies: []
enables: []
parent_master_plan:
  - M001
stakeholder: Engineering Leadership
---

## Goal

Teams need visibility into plan health, dependencies, and progress. This project builds:

- **Analytics dashboard**: Project metrics (fan-in, fan-out, depth, criticality)
- **Dependency graphs**: SVG visualization of project dependencies with status colors
- **Bottleneck analysis**: Identify blocking projects and long dependency chains
- **Timeline phases**: Compute parallel execution phases based on dependencies
- **Burndown charts**: Track completion velocity and estimate accuracy
- **Impact analysis**: Identify highest-impact projects that unblock others

## Scope

- Analytics data collection (metrics, bottlenecks, impact)
- Bottleneck detection (cycles, deep chains, high fan-out)
- Timeline phase computation
- SVG graph rendering with phase-based columns
- Web dashboard for interactive exploration
- Static HTML report generation

## Linked

- **Designs**: D007 (Analytics Architecture) — written retroactively 2026-08-30, see its Log
- **Actions**:
  - A014 — never actually created as its own action; metrics computation happened as part of general P007 work rather than a separately tracked action
  - A015: SVG dependency graph visualization (IN_PROGRESS — mostly done, see its own Log)
  - A016 — this ID was speculatively planned here on 2026-08-24 but was never created under P007; it was later used for an unrelated P009 drive-by fix (tree-view click bugs). "Create analytics dashboard UI" happened, just untracked by a dedicated action.

## Tasks

### Phase 1: Metrics & Analysis
- [x] Compute fan-in, fan-out, depth for each project
- [x] Implement bottleneck detection
- [x] Calculate project criticality scores
- [x] Implement impact analysis — `impact.py`'s `analyze_impact()`, used by `/api/analytics/<project_id>`

### Phase 2: Visualization
- [ ] Build SVG graph renderer for dependencies — the renderer itself is built (`report.py`), but static-report-only; not wired into the live dashboard, which is what this task actually means. Leaving unchecked. See A015/D007.
- [x] Generate timeline phase diagram — `gantt.py`'s Gantt chart, computed from `stats.compute_timeline`
- [x] Create burndown chart visualization — `burndown.py`, rendered live in the Analytics tab
- [x] Build interactive dashboard — the "📊 Analytics" tab itself (`analytics.js`), showing metrics + Gantt + burndown

### Phase 3: Reporting
- [x] Static HTML report generation — `plan report` / `/report`, includes the dependency-graph SVG
- [ ] Email report delivery — never started, no code exists; not referenced anywhere else in the plan either, worth deciding if this is still wanted
- [ ] Historical tracking and trends — never started; would need a place to persist a time series, which nothing in lplan does today

## Log

2026-08-30 — Aligned with actual current state at user request. Found this project was far more complete than its stale IN_PROGRESS/2026-08-24 record suggested: 7 of 9 original tasks are done (impact analysis, Gantt, burndown, and the interactive dashboard itself were all built, just never checked off here). The one genuinely unfinished visualization item is A015 (dependency-graph SVG exists but isn't wired into the live dashboard — see its Log and D007's Open Questions). Fixed the dangling `D007` design reference (never existed until now) and the two speculative Action IDs (A014, A016) that were reused elsewhere. Left IN_PROGRESS — A015's live-dashboard integration and the two Phase 3 items (email delivery, historical trends) are real gaps, not just bookkeeping.
2026-08-24 — Metrics and analysis core complete. Visualization in progress.
2026-08-23 — Project started with analytics architecture design.
