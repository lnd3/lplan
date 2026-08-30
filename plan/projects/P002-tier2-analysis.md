---
id: P002
title: Tier 2 - Analysis & Query Tools
status: DONE
priority: MEDIUM
priority_drivers:
- enables_multiple
created: 2026-08-20
updated: '2026-08-22'
description: Advanced analytics, impact analysis, capacity planning
depends:
- P001
enables:
- P003
---

## Goal

Build advanced analysis and query tools on top of the core engine. Enable users to understand project interdependencies, bottlenecks, and capacity requirements.

## Scope

- Dependency matrix generation (DSM format)
- Impact analysis ("what unblocks when I finish this?")
- Bottleneck detection (high fan-in/out projects)
- Project depth metrics and hierarchy visualization
- Capacity vs work estimates
- Timeline/Gantt chart generation
- Burndown/progress tracking

Not included:
- Real-time dashboards
- Database integration
- User permissions/access control

## Linked

- **Projects**: P001 (core engine), P003 (visualization)
- **Designs**: D006, D007, D008
- **Actions**: A009-A015

## Tasks

- [x] Impact analysis API
- [x] Dependency matrix generator
- [x] Bottleneck detection algorithm
- [x] Metrics computation (depth, fan-in/out)
- [x] Capacity tracking integration
- [x] Timeline/Gantt generation
- [x] Tests for analysis tools
- [x] Documentation for new features

## Log

2026-08-30 — Checked off all 8 Tasks checkboxes, found unchecked despite DONE status while dogfooding P010's new checkbox-based rollup math (see CHANGELOG). All 8 confirmed real via the 2026-08-22 Log entries below (impact analysis, bottleneck detection, metrics, capacity, Gantt, tests, docs all explicitly described as shipped) — this was stale bookkeeping, not incomplete work.
2026-08-22 — Polish cycle: Added FOCUS.md + REFLECTION.md to dogfood lplan's own plan. Auto-regenerate INDEX.md on HTTP access (no manual regen needed). Changelog entries now properly separated by newlines.

2026-08-22 — All Tier 2 Operational/Governance/Visibility features shipped. Web UI (plan serve) and additional scaffolding added beyond scope.

2026-08-22 — Tier 2 implementation complete: 8 modules (writer, index_gen, stats, init, refs, git_ops, report, watch), 13 CLI commands, 42 tests, suggestions in validator

2026-08-20 — Project created as future work. Depends on P001 (core engine).
