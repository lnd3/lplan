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

- **Designs**:
  - D008: Cross-Repo Architecture (not yet created — see Log 2026-08-30)
  - D005: Template File Family Scaling (DONE) — filed here as the nearest home when created; scope is actually local file-organization, not cross-repo. See Log.
- **Actions**:
  - A017, A018, A019 — these IDs were speculatively planned here on 2026-08-24 but were never created under P008; they were later used for unrelated P009 drive-by fixes (root badges, editor bugs, thesis/master_plan display). This project's Phase 1–3 tasks below remain unimplemented.
  - A026: D005 Tooling Implementation (DONE)

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

2026-08-30 — D005 (Template File Family Scaling) landed filed under this project, but its actual scope (a local file-organization convention for template-instantiated files) doesn't match P008's Goal/Scope (cross-repo coordination) at all — likely filed here simply because P008 was the only PLANNING project available at the time. Left as-is rather than moved, since a dedicated project wasn't warranted for one design+action; flagged here for whoever picks up real cross-repo work next, so it's not mistaken for part of this project's actual scope.
2026-08-24 — Project planning phase. Architecture discussion with team.
