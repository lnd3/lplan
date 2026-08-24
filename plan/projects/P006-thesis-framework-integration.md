---
id: P006
title: Thesis Framework Integration
status: DONE
priority: MEDIUM
priority_drivers:
  - strategic_edge
  - team_engagement
created: 2026-08-23
updated: 2026-08-24
description: Integrate Thesis entities (T-prefix) for capturing foundational beliefs and hypotheses driving planning decisions.
depends:
  - P001
  - P005
external_dependencies: []
enables: []
parent_master_plan:
  - M001
stakeholder: Engineering Leadership
---

## Goal

Strategic decisions rest on foundational beliefs and hypotheses. This project introduces:

- **Thesis entity type** (T-prefix IDs): Foundational beliefs, conviction level, status (HELD/QUESTIONING/ABANDONED)
- **Evidence tracking**: Theses capture rationale behind architectural decisions
- **Conviction levels**: 1-10 scale indicating confidence in each belief
- **Linkage to master plans**: Theses can link to multiple master plans they inform
- **Many-to-many relationships**: Master plans can be influenced by multiple theses

Example theses created:
- T001: Planning tools must separate strategic vision from tactical execution
- T002: Schema-driven planning enables validation and consistency
- T003: Web-based visualization improves planning accessibility

## Scope

- New Thesis Pydantic model with conviction (1-10), status (HELD/QUESTIONING/ABANDONED)
- Parser support for T-prefix IDs and theses/ directory
- Template for scaffolding new theses
- Hierarchy support showing theses → master_plans → projects
- Index template updated with Theses section
- Status view includes thesis filter

## Linked

- **Designs**: D006: Thesis Framework Architecture
- **Actions**:
  - A011: Implement Thesis model
  - A012: Add thesis support to parser
  - A013: Create example theses

## Tasks

### Phase 1: Core Implementation
- [x] Design Thesis model with conviction and status fields
- [x] Update parser to recognize T-prefix IDs
- [x] Update hierarchy building to include theses

### Phase 2: UI Integration
- [x] Add theses to Tree view hierarchy
- [x] Add theses to Status view with conviction filtering
- [x] Update INDEX template with Theses section

### Phase 3: Examples & Documentation
- [x] Create T001 (Vision-Execution Separation)
- [x] Create T002 (Schema-Driven Planning)
- [x] Create T003 (Visualization Accessibility)

## Log

2026-08-24 — Thesis framework fully integrated. Example theses document lplan's evolution.
2026-08-23 — Core implementation and parser integration complete.
