---
id: P005
title: Master Plans & Strategic Vision Architecture
status: DONE
priority: HIGH
priority_drivers:
  - critical_live_path_only
created: 2026-08-22
updated: 2026-08-24
description: Implement cross-repo distribution of strategic visions and goals via MasterPlan entities.
depends:
  - P001
  - P004
external_dependencies: []
enables:
  - P006
  - P008
parent_master_plan:
  - M001
stakeholder: Engineering Leadership
---

## Goal

Organizations need a way to declare strategic visions and goals that multiple repos can implement. This project introduces:

- **MasterPlan entity type** (M-prefix IDs): Strategic vision, goals, stakeholder, scope
- **Parent linkage**: Projects declare which master plans they serve via parent_master_plan field
- **Cross-repo pattern**: Upstream repos define master plans; downstream repos implement them
- **Separation of concerns**: Strategy (upstream) vs execution (downstream) clearly separated
- **Full UI integration**: Master plans visible in Files view, Tree view, Items view, INDEX

Example master plans created:
- M001: Developer Experience Excellence (Engineering Leadership)
- M002: Scalability Foundation (Infrastructure Team) — moved to the accessibility-lplan repo 2026-08-30; not part of lplan's own plan anymore, see Log

## Scope

- New MasterPlan Pydantic model with stakeholder, vision, goals, scope fields
- Parser support for M-prefix IDs and master_plans/ directory
- Template for scaffolding new master plans
- Project model enhancements: parent_master_plan field
- API endpoints support master plans in status view
- UI support across Files, Tree, Items views
- INDEX.md template and examples updated

## Linked

- **Designs**: D005: MasterPlan Architecture Design
- **Actions**:
  - A008: Implement MasterPlan model
  - A009: Add master_plans to all views
  - A010: Create example master plans

## Tasks

### Phase 1: Core Implementation
- [x] Design MasterPlan model and schema
- [x] Update parser to recognize M-prefix IDs
- [x] Implement _parse_master_plan method
- [x] Update Project model with parent_master_plan field

### Phase 2: API & Views
- [x] Update /api/status endpoint for master plans
- [x] Add master_plans to /api/tree endpoint
- [x] Add master_plans to /api/hierarchy endpoint
- [x] Update Items view UI to show master plans

### Phase 3: UI & Navigation
- [x] Add master plans to Files view (FileBrowser)
- [x] Add master plans section to Tree view
- [x] Update Entity viewer for master_plan type
- [x] Polish Tree view layout (bullet points, no indentation)

### Phase 4: Examples & Documentation
- [x] Create M001 (Developer Experience Excellence)
- [x] Create M002 (Scalability Foundation) — later moved to accessibility-lplan repo, no longer here
- [x] Create master_plan.md.template
- [x] Update INDEX.md.template with Master Plans section

## Log

2026-08-30 — M002 (Scalability Foundation) moved to the accessibility-lplan repo, at user request — it's irrelevant to lplan's own plan. Removed from parent_master_plan here and from P008/T001/T002; deleted plan/master_plans/M002-scalability-foundation.md itself.
2026-08-24 — All views updated. Master plans fully integrated and navigable.
2026-08-24 — Core implementation and API support complete.
2026-08-22 — Project started. Architecture designed with team.
