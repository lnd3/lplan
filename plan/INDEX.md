# lplan Plan Index

*Last updated: 2026-08-28 11:31:13 UTC*

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
| [M001](master_plans/M001-developer-experience.md) | Developer Experience Excellence | IN_PROGRESS | HIGH |
| [M002](master_plans/M002-scalability-foundation.md) | Scalability Foundation | PLANNING | HIGH |

---

## Projects

| ID | Title | Status | Priority | Key Open Work |
| --- | --- | --- | --- | --- |
| [P001](projects/P001-tier1-engine.md) | Tier 1 - Python Execution Engine | DONE | HIGH | TBD |
| [P002](projects/P002-tier2-analysis.md) | Tier 2 - Analysis & Query Tools | DONE | MEDIUM | TBD |
| [P003](projects/P003-tier3-automation.md) | Tier 3 - Automation & Visualization | DONE | MEDIUM | TBD |
| [P004](projects/P004-web-server-ui-refactoring.md) | Web Server & UI Refactoring | DONE | HIGH | TBD |
| [P005](projects/P005-master-plans-strategic-vision.md) | Master Plans & Strategic Vision Architecture | DONE | HIGH | TBD |
| [P006](projects/P006-thesis-framework-integration.md) | Thesis Framework Integration | DONE | MEDIUM | TBD |
| [P007](projects/P007-analytics-reporting-dashboard.md) | Analytics & Reporting Dashboard | IN_PROGRESS | MEDIUM | TBD |
| [P008](projects/P008-cross-repo-planning-integration.md) | Cross-Repo Planning Integration | PLANNING | MEDIUM | TBD |
| [P009](projects/P009-external-maintenance.md) | External Maintenance | IN_PROGRESS | LOW | TBD |
| [P010](projects/P010-plan-health-dashboard.md) | Plan Health Dashboard | IN_PROGRESS | HIGH | TBD |

---

## Designs

| ID | Title | Status | Project | Doc |
| --- | --- | --- | --- | --- |
| [D001](designs/D001-priority-engine.md) | Priority Scoring Engine Design | DONE | P001 | (link if applicable) |
| [D002](designs/D002-dependency-graph.md) | Dependency Graph Analysis Design | DONE | P001 | (link if applicable) |
| [D003](designs/D003-javascript-module-architecture.md) | JavaScript Module Architecture | DONE | P004 | (link if applicable) |
| [D004](designs/D004-plan-health-dashboard-architecture.md) | Plan Health Dashboard Architecture | DONE | P010 | (link if applicable) |

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
| [A023](actions/A023-status-overview-dogfood.md) | Dogfood against lplan's own plan/ | IN_PROGRESS | D004 | TBD |