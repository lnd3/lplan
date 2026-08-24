---
id: P008
title: Cross-Repo Planning Integration
status: PLANNING
priority: MEDIUM
priority_drivers:
  - strategic_edge
  - team_engagement
created: 2026-08-24
updated: 2026-08-24
description: Enable coordination of plans across multiple repositories with upstream/downstream dependencies and shared master plans.
depends:
  - P001
  - P005
  - P006
external_dependencies: []
enables: []
parent_master_plan:
  - M001
  - M002
stakeholder: Engineering Leadership
---

## Goal

Large organizations run multiple repositories that need coordinated planning. This project enables:

- **Cross-repo references**: Projects can declare dependencies on repo:ID format
- **Shared master plans**: Downstream repos fetch and implement upstream master plans
- **Dependency validation**: Detect broken cross-repo references and missing upstream repos
- **Aggregated views**: See plan status across multiple repos in one dashboard
- **Consistency checking**: Ensure cross-repo dependencies are satisfied

## Scope

- Cross-repo reference syntax (repo:ID)
- Upstream repo detection and validation
- Shared master plan distribution and import
- Aggregated analytics across repos
- CLI commands for repo discovery and sync
- Conflict resolution for competing master plans

## Linked

- **Designs**: D008: Cross-Repo Architecture
- **Actions**:
  - A017: Implement repo reference resolution
  - A018: Build cross-repo validation
  - A019: Create repo sync mechanism

## Tasks

### Phase 1: Reference Resolution
- [ ] Implement repo:ID syntax parsing
- [ ] Discover sibling repos via file system walk
- [ ] Resolve cross-repo references with fallback

### Phase 2: Master Plan Distribution
- [ ] Implement master plan import from upstream repos
- [ ] Cache upstream master plans locally
- [ ] Detect and warn on master plan conflicts

### Phase 3: Aggregation
- [ ] Build cross-repo analytics aggregator
- [ ] Create unified status view across repos
- [ ] Implement dependency chain validation

## Log

2026-08-24 — Project planning phase. Architecture discussion with team.
