# Project File Schema

A project file defines a high-level goal, scope, and task list.

## Location & Naming
- Location: `plan/projects/`
- Naming: `P<NNN>-kebab-case-title.md`
- Examples: `P001-price-levels-strategy.md`, `L001-node-registry.md`, `D001-build-system.md`

## Required Frontmatter Fields
- `id`: P001, P002, etc.
- `title`: Human-readable goal
- `status`: IDEA, PLANNING, IN_PROGRESS, BLOCKED, DONE, DEFERRED, CANCELLED
- `priority`: HIGH, MEDIUM, LOW
- `priority_drivers`: List of driver keys from priority-framework.md
- `created`: YYYY-MM-DD
- `updated`: YYYY-MM-DD

## Optional Frontmatter Fields
- `depends`: List of "repo:ID" projects this depends on
- `external_dependencies`: List of external repo features needed
- `enables`: List of "repo:ID" projects this unblocks
- `project`: Parent project if nested
- `description`: One-line summary for INDEX

## Content Sections (After Frontmatter)

All project files should have these sections (in order):

### ## Goal
1–2 paragraph statement of what this project achieves. Answer: "What is this trying to accomplish?"

### ## Scope
Bullet-point list of what's included and excluded. What repos/systems does it touch?

### ## Linked
Reference to related projects, designs, actions, and external dependencies.

Format:
```markdown
- **Projects**: P001, P002 (projects this depends on)
- **Designs**: D001, D002 (designs this implements)
- **Actions**: A001 (concrete tasks for this project)
- **Dependencies**: ltools (upstream), ldeps (upstream)
```

### ## Tasks
Checklist of major milestones or work items. Use `- [ ]` for uncompleted, `- [x]` for done.

Optionally grouped by phase, component, or category.

```markdown
## Tasks

### Core Implementation
- [x] Feature A
- [ ] Feature B
- [ ] Feature C

### Validation
- [ ] Unit tests
- [ ] Integration tests
```

### ## Log
Append-only changelog for this project. When status changes, add an entry.

Format: `YYYY-MM-DD — Brief note on what changed or was decided.`

Example:
```markdown
## Log

2026-08-20 — Project created. VolumeLevels V3 shipped; tuning pending.
2026-05-30 — Initial scope defined; design complete.
```

## Hierarchy & Dependencies

- **Project** → **Design** → **Action**
  - Projects are goals
  - Designs are detailed specifications
  - Actions are concrete task lists to implement designs
  - Reference via frontmatter: Project lists `design: D001` in its links

- **Cross-Repo Dependencies**
  - Use `depends: ["ltools:L001", "ldeps:D001"]` to declare
  - Aggregator resolves refs and shows impact
  - Update status when dependency completes or changes

## Priority Computation

`priority` is computed from `priority_drivers` using the framework's scoring rules (see priority-framework.md).

When drivers change:
1. Recalculate score
2. Update `priority` field
3. Update `updated` date
4. Append to Log section
5. Commit to CHANGELOG.md in repo root

Example:
```yaml
priority_drivers:
  - critical_live_path_only    # +2.5
# Score: 2.5 → HIGH
priority: HIGH
```

## Validation

A valid project file must:
- [ ] Have all required frontmatter fields
- [ ] Have non-empty Goal, Scope, Tasks sections
- [ ] Have valid YAML frontmatter
- [ ] Have valid cross-repo refs (resolvable via file system or repo registry)
- [ ] Have status in enum list
- [ ] Have priority in enum list
- [ ] Have priority_drivers that match framework definitions
- [ ] Have created ≤ updated (dates)

Run: `validate.sh plan/projects/P001.md`

## Example

```yaml
---
id: P005
title: HyperLiquid API Integration
status: PLANNING
priority: HIGH
priority_drivers:
  - critical_live_path_only
created: 2026-08-20
updated: 2026-08-20
depends: []
external_dependencies:
  - repo: ltools
    feature: "Node IDs 10600+ reserved"
    status: "DONE"
    blocking: false
enables:
  - tradeflow:P001
---

## Goal

Integrate HyperLiquid exchange API for live paper and real trading. Enable real-time market data ingestion, order placement, and position management via AutoTraderSys.

## Scope

- HyperLiquid WebSocket connection and data streaming
- Authentication and account management
- Order submission and management
- Position tracking and P&L calculation
- Integration with AutoTraderSys for automated execution

## Linked

- **Projects**: P001 (Price Levels Strategy; this enables it)
- **Designs**: (TBD)
- **Actions**: (TBD)
- **Dependencies**: ltools (node graph), ldeps (build system)

## Tasks

- [ ] API research and endpoint mapping
- [ ] WebSocket connection handler
- [ ] Order placement implementation
- [ ] Position management
- [ ] AutoTraderSys integration
- [ ] Paper trading validation
- [ ] Live trading integration

## Log

2026-08-20 — Project created. IDEA status; critical path escalated to PLANNING due to Binance unavailability.
```
