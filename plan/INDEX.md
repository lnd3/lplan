# lplan Plan Index

*Last updated: 2026-09-01 13:06:18 UTC*

Status: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

---

## Concepts

| ID | Title | Type | Status |
| --- | --- | --- | --- |
| [C001](concepts/C001-hierarchical-entity-model.md) | Hierarchical Entity Model | pattern | STABLE |
| [C002](concepts/C002-modular-architecture.md) | Modular Architecture | pattern | STABLE |
| [C003](concepts/C003-event-delegation.md) | Event Delegation Pattern | pattern | STABLE |
| [C004](concepts/C004-dependency-graph-analysis.md) | Dependency Graph Analysis | pattern | STABLE |
| [C005](concepts/C005-yaml-frontmatter-format.md) | YAML Frontmatter Format | rule | STABLE |

---

## Theses

| ID | Title | Status | Conviction |
| --- | --- | --- | --- |
| [T001](theses/T001-planning-vision-execution-separation.md) | Planning Tools Must Separate Strategic Vision from Tactical Execution | HELD | 9 |
| [T002](theses/T002-schema-driven-planning-validation.md) | Schema-Driven Planning Enables Validation and Consistency | HELD | 9 |
| [T003](theses/T003-visualization-improves-accessibility.md) | Web-Based Visualization Improves Planning Accessibility and Engagement | HELD | 8 |

---

## Master Plans

| ID | Title | Status | Priority |
| --- | --- | --- | --- |
| [M001](master_plans/M001-developer-experience.md) | lplan Framework Development | IN_PROGRESS | HIGH |

---

## Projects

| ID | Title | Status | Priority | Key Open Work |
| --- | --- | --- | --- | --- |
| [P001](projects/P001-tier1-engine.md) | Tier 1 - Python Execution Engine | IN_PROGRESS | HIGH | TBD |
| [P002](projects/P002-tier2-analysis.md) | Tier 2 - Analysis & Query Tools | DONE | MEDIUM | TBD |
| [P003](projects/P003-tier3-automation.md) | Tier 3 - Automation & Visualization | DONE | MEDIUM | TBD |
| [P004](projects/P004-web-server-ui-refactoring.md) | Web Server & UI Refactoring | DONE | HIGH | TBD |
| [P005](projects/P005-master-plans-strategic-vision.md) | Master Plans & Strategic Vision Architecture | IN_PROGRESS | HIGH | TBD |
| [P006](projects/P006-thesis-framework-integration.md) | Thesis Framework Integration | DONE | MEDIUM | TBD |
| [P007](projects/P007-analytics-reporting-dashboard.md) | Analytics & Reporting Dashboard | IN_PROGRESS | MEDIUM | TBD |
| [P008](projects/P008-cross-repo-planning-integration.md) | Cross-Repo Planning Integration | PLANNING | MEDIUM | TBD |
| [P009](projects/P009-external-maintenance.md) | External Maintenance | IN_PROGRESS | LOW | TBD |
| [P010](projects/P010-plan-health-dashboard.md) | Plan Health Dashboard | DONE | HIGH | TBD |

---

## Designs

| ID | Title | Status | Project | Doc |
| --- | --- | --- | --- | --- |
| [D001](designs/D001-priority-engine.md) | Priority Scoring Engine Design | DONE | P001 | (link if applicable) |
| [D002](designs/D002-dependency-graph.md) | Dependency Graph Analysis Design | DONE | P001 | (link if applicable) |
| [D003](designs/D003-javascript-module-architecture.md) | JavaScript Module Architecture | DONE | P004 | (link if applicable) |
| [D004](designs/D004-plan-health-dashboard-architecture.md) | Plan Health Dashboard Architecture | DONE | P010 | (link if applicable) |
| [D005](designs/D005-template-file-family-scaling.md) | Template File Family Scaling 📎 _see also: `D005_learnings.md`_ | DONE | P008 | (link if applicable) |
| [D007](designs/D007-analytics-architecture.md) | Analytics Architecture | DONE | P007 | (link if applicable) |
| [D008](designs/D008-project-phase-action-linking.md) | Project Phase → Design/Action Linking (Loose Coupling) | IN_PROGRESS | P001 | (link if applicable) |
| [D009](designs/D009-master-plan-priority-stack.md) | Master Plan Priority Stack | IDEA | P005 | (link if applicable) |

---

## Actions

| ID | Title | Status | Design | Open Tasks |
| --- | --- | --- | --- | --- |
| [A001](actions/A001-priority-engine-tests.md) | Implement Priority Engine Tests | DONE | D001 | TBD |
| [A004](actions/A004-extract-ui-modules.md) | Extract UI utility module from monolithic server.py | DONE | D003 | TBD |
| [A008](actions/A008-implement-master-plan-model.md) | Implement MasterPlan Pydantic model with schema validation | DONE | D005 | TBD |
| [A011](actions/A011-implement-thesis-model.md) | Implement Thesis Pydantic model with conviction levels | DONE | D006 | TBD |
| [A015](actions/A015-implement-dependency-graph-visualization.md) | Implement SVG dependency graph visualization | IN_PROGRESS | D007 | TBD |
| [A016](actions/A016-tree-view-click-breaking-bugs.md) | Fix tree-view clicks breaking on apostrophes and duplicate master-plan DOM ids | DONE | — | TBD |
| [A017](actions/A017-root-badges-and-page-identity.md) | Root badges for all parentless items, page title/heading, reachable Save from Tree view | DONE | — | TBD |
| [A018](actions/A018-editor-and-generated-file-bugs.md) | Save/Cancel never visible in edit mode; sidebar toggle glyph stuck; INDEX.md wrongly editable | DONE | — | TBD |
| [A019](actions/A019-thesis-master-plan-content-pane-and-toggle-glyphs.md) | Thesis<->master_plan content-pane display; toggle-glyph rotation cleanup; master plans get full sidebar + children view | DONE | — | TBD |
| [A020](actions/A020-status-overview-rollup-api.md) | Backend rollup API (/api/status-overview) | DONE | D004 | TBD |
| [A021](actions/A021-status-overview-frontend.md) | Frontend overview.js module + nav tab | DONE | D004 | TBD |
| [A022](actions/A022-status-overview-needs-attention-panel.md) | Needs-attention panel (stale, blocked, dangling refs) | DONE | D004 | TBD |
| [A023](actions/A023-status-overview-dogfood.md) | Dogfood against lplan's own plan/ | DONE | D004 | TBD |
| [A024](actions/A024-memory-maintenance-workflow.md) | AI Agent Memory Maintenance — Workflow Documentation | DONE | — | TBD |
| [A025](actions/A025-consumer-repo-alignment-check.md) | Consumer Repo Structural Alignment Check | DONE | — | TBD |
| [A026](actions/A026-d005-tooling-implementation.md) | D005 Tooling Implementation — Companion File Support | DONE | D005 | TBD |
| [A027](actions/A027-validator-parent-child-consistency.md) | Validator — Parent-Child Status Consistency Check | IN_PROGRESS | — | TBD |
| [A028](actions/A028-d008-phases-1-3-implementation.md) | D008 Implementation — Phases 1–3 | DONE | D008 | TBD |
| [A029](actions/A029-status-overview-validator-warnings.md) | Surface Validator Warnings in the Status Dashboard | DONE | D004 | TBD |
| [A030](actions/A030-checkbox-based-progress.md) | Checkbox-Based Progress for Project/Master Plan Rollups | DONE | D004 | TBD |
| [A031](actions/A031-items-view-completion-sort.md) | Items View — Completion Column + Default Sort Least-Complete-First | DONE | D004 | TBD |
| [A032](actions/A032-progress-badges-and-sorted-dashboard.md) | Tree View Progress Badges, Items View Label Rename, Status Dashboard Sort | DONE | D004 | TBD |
| [A033](actions/A033-rename-status-items-views.md) | Rename Internal View Naming to Match Toolbar Buttons | DONE | D004 | TBD |
| [A034](actions/A034-skip-phase-anchors-on-terminal-projects.md) | Skip phase-anchor warnings on terminal-status projects | DONE | — | TBD |
| [A035](actions/A035-validator-duplicate-id-check.md) | Validator — Duplicate Entity ID Check | DONE | — | TBD |