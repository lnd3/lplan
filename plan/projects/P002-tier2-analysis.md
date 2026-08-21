---
id: P002
title: Tier 2 - Analysis & Query Tools
status: DONE
priority: HIGH
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

- [ ] Impact analysis API
- [ ] Dependency matrix generator
- [ ] Bottleneck detection algorithm
- [ ] Metrics computation (depth, fan-in/out)
- [ ] Capacity tracking integration
- [ ] Timeline/Gantt generation
- [ ] Tests for analysis tools
- [ ] Documentation for new features

## Log

2026-08-22 — All Tier 2 Operational/Governance/Visibility features shipped. Web UI (plan serve) and additional scaffolding added beyond scope.

2026-08-22 — Tier 2 implementation complete: 8 modules (writer, index_gen, stats, init, refs, git_ops, report, watch), 13 CLI commands, 42 tests, suggestions in validator

2026-08-20 — Project created as future work. Depends on P001 (core engine).
