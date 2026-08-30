---
id: M001
title: lplan Framework Development
status: IN_PROGRESS
stakeholder: lplan maintainers and contributors (including AI agents working across lplan and consuming repos)
vision: lplan should be the tool AI agents and their users trust to keep a software project's plan coherent — from a single repo's own backlog up through cross-repo strategic vision — without maintaining that coherence becoming a burden nobody actually does.
priority: HIGH
goals:
  - Full entity hierarchy (Thesis→MasterPlan→Project→Design→Action, plus Concepts) with validation, CLI, and web UI support for every type
  - Plan hygiene is self-enforcing via tooling (staleness/drift surfaced automatically), not reliant on manual discipline someone has to remember
  - "lplan works cleanly as a cross-repo dependency: template updates propagate without silent drift, drive-by contributions have a low-friction but reviewed path, multi-repo plans stay consistent"
  - The companion-file convention (D005) prevents the format-corruption and context-truncation failures observed in early adopter repos
created: 2026-08-20
updated: 2026-08-30
---

## Goal

lplan exists because plans rot: status goes stale, decisions get lost, and the summary documents meant to keep everyone (human or agent) oriented drift out of sync with reality — this repo's own `plan/` has hit that exact failure more than once. This master plan tracks lplan's own development as a framework: the entity model and validation that make a plan machine-checkable, the CLI and web UI that make it usable day-to-day, the workflow conventions that tell an agent *when* to touch the plan (not just *how*), and the cross-repo mechanics that let lplan serve as a shared dependency rather than a single-repo tool.

## Scope

**Included:**
- Entity model, schema validation, and the CLI built on top of it
- Web UI (`plan serve`, all views: Files, Tree, Analytics, Items, Status)
- Workflow conventions (`WORKFLOW.md`/`WORKFLOW_DETAILS.md`) and the templates that scaffold new repos
- Cross-repo distribution mechanics: template propagation, drive-by contribution handling, multi-repo consistency
- Companion-file convention (D005) and other structural conventions that keep root plan files lean

**Not included:**
- The actual planning *content* of any downstream repo (TradeFlow's, superplan's, accessibility-lplan's own plans are their business, not lplan's)
- Non-planning developer tooling not integrated with `plan validate`/the entity model (e.g. a repo's own CI/CD pipeline internals)

## Linked

- **Projects**:
  - P001: Tier 1 — Python Execution Engine (DONE)
  - P002: Tier 2 — Analysis & Query Tools (DONE)
  - P003: Tier 3 — Automation & Visualization (DONE)
  - P004: Web Server & UI Refactoring (DONE)
  - P005: Master Plans & Strategic Vision Architecture (DONE)
  - P006: Thesis Framework Integration (DONE)
  - P007: Analytics & Reporting Dashboard (IN_PROGRESS)
  - P008: Cross-Repo Planning Integration (PLANNING)
  - P009: External Maintenance (IN_PROGRESS, perpetual catch-all)
  - P010: Plan Health Dashboard (DONE)
- **Other Master Plans**: None currently. M002 (Scalability Foundation) was created alongside this one as MasterPlan-feature demo content, then moved to the accessibility-lplan repo 2026-08-30 once it became clear it described that repo's own infrastructure work, not lplan's.
- **References**: `plan/REFLECTION.md`/`REFLECTION_extension.md` (patterns and gotchas from building this), `plan/CHANGELOG.md` (full decision trail)

## Tasks

### Phase 1 — Foundation (DONE)
- [x] P001: Programmatic planning engine (models, parser, validator, priority, graph)
- [x] P002: Analysis & query tooling
- [x] P003: Automation & visualization (Gantt/burndown SVG, report generation)

### Phase 2 — Structure & Web UI (DONE)
- [x] P004: Extract monolithic server.py into modular Flask + JS
- [x] P005: MasterPlan entity + cross-repo distribution architecture
- [x] P006: Thesis entity + many-to-many thesis↔master_plan relationships
- [x] Concept entity type (C001–C005) added post-hoc, not originally scoped as its own project

### Phase 3 — Visibility & Plan Health (mostly DONE)
- [x] P010: Plan Health Dashboard — hierarchy-wide rollups + stale/blocked/dangling-ref surfacing, closing the exact drift problem this master plan's vision names
- [ ] P007: Analytics & Reporting Dashboard — metrics/impact/bottleneck/Gantt/burndown all live; remaining scope is wiring the dependency-graph SVG (currently static-report-only, see D007) into the live dashboard, plus historical trend tracking (not started)

### Phase 4 — Cross-Repo Maturity (upcoming)
- [ ] P008: Cross-repo reference resolution, upstream master plan sync, aggregated multi-repo status — real scope, still unstarted despite D005 having been mistakenly filed under it
- [ ] D005 (Template File Family Scaling) adoption across consuming repos — built and dogfooded here 2026-08-30; propagating it (and the Consumer Repo Structural Alignment Check, A025) to TradeFlow/superplan/accessibility-lplan is still manual
- [ ] Historical/time-series tracking for plan health (explicitly deferred out of P010's scope; would need somewhere to persist a time series, which nothing in lplan does today — see D007's Constraints)
- [ ] Revisit whether the External Contribution Workflow's policy-change tightening (2026-08-30) is holding up as more repos contribute drive-by

## Log

2026-08-30 — Rewritten at user request to be lplan's actual master plan. Original content (generic "5-year DX vision," fabricated Q2 2026 survey, latency/satisfaction targets with no connection to lplan) was demo content created 2026-08-20 alongside M002 specifically to exercise the then-new MasterPlan entity type, never lplan's real strategic tracking. M002 got the same treatment first (moved out once its content turned out to describe accessibility-lplan's actual infrastructure work) — M001 turned out to be pure placeholder with nowhere else to go, so it's rewritten in place instead. Phases above map to the real, already-substantially-complete arc of P001–P010.
2026-08-30 — P010 (Plan Health Dashboard) completed — one of this master plan's contributing projects now DONE.
2026-08-24 — Master plan created. Establishing strategic direction for DX improvements across the org.
2026-08-20 — Planning phase. Initial stakeholder interviews completed.
