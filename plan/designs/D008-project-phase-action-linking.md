---
id: D008
title: Project Phase → Action/Design Linking
status: PLANNING
priority: MEDIUM
project: P001
created: 2026-08-30
updated: 2026-08-30
---

## What

A mechanism to declare which phase of a parent Project an Action or Design belongs to.
This enables `generate-index` (or a new `plan check-phases` command) to automatically
reconstruct the phase breakdown in a project file from its child entities, rather than
maintaining it by hand.

## Why

Project files currently contain detailed task checklists organised into phases (e.g.
`### Phase 1 — Strategy Pipeline`). Those checklists are maintained manually and drift
from reality:

- Completed tasks remain unchecked (invisible to the rollup) when an Action is closed
  without updating the parent project file.
- New tasks are added to the project file instead of creating an Action, making them
  invisible to the child-entity status rollup.
- The status view shows "X/Y children done" based only on entity relationships, not on
  the in-file checkbox state, producing a false "complete" signal.

Root case: TradeFlow P001 showed "all children DONE" (A001, A003, A012 all DONE) while
the project file still had 8 unchecked tasks across three phases. A013 was created to
capture those tasks and make the gap visible — but the gap should be structurally
impossible to create in the first place.

## How

### Minimal — `phase` frontmatter field on Actions and Designs

```yaml
id: A013
project: P001
phase: "Phase 3 — V3 Tuning, Real Data Validation, Cleanup"
```

`generate-index` and the health dashboard use this to build the phase view from
children rather than from the project file body. Project file's `## Phases` section
becomes a generated artifact (like `INDEX.md`), not a hand-maintained checklist.

Generated output per project:

```markdown
## Phases (generated)

| Phase | Owner | Status | Open tasks |
|---|---|---|---|
| Phase 1 — Strategy Pipeline | A001, A003 | DONE | 0 |
| Phase 2 — Backtest Validation | A012 | DONE | 0 |
| Phase 3 — V3 Tuning | A013 | IN_PROGRESS | 3 |
```

"Open tasks" is the count of `- [ ]` items in the owning Action/Design file —
making in-file checkbox completion visible alongside the entity status rollup.

### Extended — checkbox extraction

`generate-index` already reads frontmatter and body. Parsing `- [x]` / `- [ ]`
counts per file is straightforward. This exposes in-file completion as a
supplementary signal without replacing the primary child-entity rollup.

## Constraints

- `phase` is optional — existing Actions/Designs without it remain valid.
- Phase names are free-form strings matched against the project's declared phase list.
  Typos → unmatched (validator warns). No enum, no schema migration.
- Projects that don't use phases are unaffected. The generated `## Phases` section
  only appears if at least one child has a `phase` field.
- The project file's hand-written `## Phases` / `## Tasks` section is replaced by
  the generated one; any manual notes belong in `## Notes` instead.

## Phases

- **Phase 1 (PLANNING)**: Add `phase` field to Action/Design models + validator
- **Phase 2 (PLANNING)**: `generate-index` reads `phase` field, emits phase table per project
- **Phase 3 (PLANNING)**: Checkbox extraction — count `[ ]` / `[x]` per file, include in table
- **Phase 4 (PLANNING)**: Health dashboard phase view (mirrors generate-index output)

## Log

2026-08-30 — Design filed from TradeFlow context. P001 had 8 unchecked tasks invisible
  to the rollup; A013 created as a workaround. The correct fix is structural: phases
  declared on children, project file generated from them. Minimal path is a `phase`
  frontmatter field + generate-index change; checkbox extraction is a natural extension.
