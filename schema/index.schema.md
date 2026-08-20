# INDEX.md Schema

The INDEX.md file is the master dashboard for a repository's planning. It provides at-a-glance status and links to detailed project/design/action files.

## Purpose

- **Status overview**: Current state of all projects, designs, actions
- **Priority view**: See what's HIGH, MEDIUM, LOW
- **Navigation**: Links to detailed files
- **Dependency visibility**: Show what's blocking what
- **Context**: Explain the planning framework

## Structure

Each INDEX.md follows this order:

### Header
```markdown
# [Repo Name] Plan Index

*Last updated: YYYY-MM-DD*

Status: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

---
```

### Priority Framework (Optional, if custom)
If the repo overrides or extends lplan's priority system, include:
```markdown
## Priority Framework

[Description of local drivers, scoring, etc.]
[Can inherit from `.lplan/schema/priority-framework.md` with local additions]
```

### Projects Table
```markdown
## Projects

| ID | Title | Status | Priority | Key Open Work |
| --- | --- | --- | --- | --- |
| [P001](projects/P001-price-levels-strategy.md) | Price Levels Strategy | BLOCKED | HIGH | Ready; blocked by P005/P006 |
| [P002](projects/P002-sub-bar-simulation.md) | Sub-Bar Simulation | IN_PROGRESS | MEDIUM | Phase 9 signal pipeline |
```

**Columns**:
- `ID`: Link to project file
- `Title`: From project frontmatter
- `Status`: From project frontmatter
- `Priority`: Computed from priority_drivers
- `Key Open Work`: 1-line summary of blockers/next steps

### Designs Table
```markdown
## Designs

| ID | Title | Status | Project | Doc |
| --- | --- | --- | --- | --- |
| [D001](designs/D001-anchored-levels.md) | Anchored Volume Levels V3 | DONE | P001 | `docs/anchored_levels_design.md` |
```

**Columns**:
- `ID`: Link to design file
- `Title`: From design frontmatter
- `Status`: From design frontmatter
- `Project`: Parent project ID (from frontmatter)
- `Doc`: Link to full design doc (if exists)

### Actions Table
```markdown
## Actions

| ID | Title | Status | Design | Open Tasks |
| --- | --- | --- | --- | --- |
| [A001](actions/A001-signal-node-correctness.md) | Signal Correctness — Post-Audit Items | IN_PROGRESS | D002 | 3 fixes + pyramiding |
```

**Columns**:
- `ID`: Link to action file
- `Title`: From action frontmatter
- `Status`: From action frontmatter
- `Design`: Parent design ID (if applicable)
- `Open Tasks`: Count or summary

### Linked Submodule Plans (Optional)
If repo has submodules with their own `plan/` directories:

```markdown
## Linked Submodule Plans

### ltools (deps/ltools/)
| ID | Title | Status | Priority | Impact on [Repo] |
| --- | --- | --- | --- | --- |
| [L001](../deps/ltools/plan/projects/L001.md) | Node Registry Overhaul | DONE | — | P005 depends; available ✓ |

**Status**: No current blockers.

### ldeps (deps/ldeps/)
| ID | Title | Status | Priority | Impact |
| --- | --- | --- | --- | --- |
| [D001](../deps/ldeps/plan/projects/D001.md) | CUDA Glob Fix | DEFERRED | LOW | Build workaround in place |
```

### Priority Rationale (Optional)
If priorities have changed or are non-obvious:

```markdown
## Priority Rationale

### P001: Price Levels Strategy — BLOCKED (-1.5 pts)
**Drivers**: `strategic_edge` (+1.0), `blocked_on_infrastructure` (-2.5)  
Strategy is complete; blocked by unavailable exchange integration (Binance EU MiCA). Unblocks when P005/P006 completes.

### P005: HyperLiquid API Integration — HIGH (2.5 pts)
**Drivers**: `critical_live_path_only` (+2.5)  
One of two critical paths to live trading. Must start immediately.
```

### Suggested Next Session (Optional)
Prioritized list of recommended work for next session:

```markdown
## Suggested Next Session

1. **P005 Design** — HyperLiquid API architecture
2. **A001/A003** — Quick fixes ready to deploy once P005 unblocks
3. **A002 Phase 9** — Independent sub-bar signal pipeline work
```

---

## Auto-Generation

Some repos may auto-generate INDEX.md from project/design/action files. If so:

1. Store metadata in frontmatter (status, priority, title)
2. Run aggregation tool: `./tools/aggregate-local.sh`
3. Tool reads all frontmatter, generates INDEX.md
4. Commit both source files and INDEX.md

Manual maintenance is also valid; choose based on repo needs.

## Maintenance

- Update `*Last updated*` timestamp when INDEX changes
- Update tables when projects change status/priority
- Add to "Suggested Next Session" when priorities shift
- Keep in sync with project file frontmatter (they are source; INDEX is view)

## Example

See `../examples/INDEX.md.example` for a complete, populated example.
