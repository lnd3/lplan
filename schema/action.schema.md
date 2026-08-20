# Action File Schema

An action file tracks concrete implementation tasks to build what a design specifies.

## Location & Naming
- Location: `plan/actions/`
- Naming: `A<NNN>-kebab-case-title.md`
- Examples: `A001-signal-node-correctness.md`, `A002-sub-bar-simulation.md`

## Required Frontmatter Fields
- `id`: A001, A002, etc.
- `title`: Action title
- `status`: IDEA, PLANNING, IN_PROGRESS, BLOCKED, DONE, DEFERRED, CANCELLED
- `created`: YYYY-MM-DD
- `updated`: YYYY-MM-DD

## Optional Frontmatter Fields
- `design`: Parent design ID (e.g., D002)
- `project`: Associated project ID
- `priority`: If action is independent (not tied to design)
- `depends`: List of "repo:ID" actions/projects this depends on
- `description`: One-line summary

## Content Sections

### ## Context
Why does this action exist? What design or project does it implement? Reference design/project files.

### ## Tasks
Detailed, actionable checklist. Use `- [ ]` and `- [x]`.

Organize into:
- **Phases** (if work is staged)
- **Categories** (by component or concern)
- **Priority** (quick/low-effort items vs. substantial)

Each task should be:
- Specific (what exactly needs to be done?)
- Assignable (who does it?)
- Testable (how do we know it's done?)

Example:
```markdown
## Tasks

### Phase 1 — Quick Wins
- [ ] **Fix A**: DCASignalV2 `shrink_to_fit()` anti-pattern (file: NGDataIODCASignals.cpp)
- [ ] **Fix B**: BacktestMetrics missing `subBarSourceReal` field (file: BacktestMetrics.h)

### Phase 2 — Substantial Work
- [ ] Implement DCALotManager.UpdateMostRecentOpenEntry()
- [ ] Add pyramiding support to AutoTraderSys
- [ ] Unit test DCASignalV3PyramidTest.cpp
```

### ## Log
Append-only record of progress.

Format: `YYYY-MM-DD — Status update or decision.`

Example:
```markdown
## Log

2026-08-20 — Action created. Phases 1–3 complete; post-audit items remain.
2026-05-15 — Fix A completed; Fix B started.
```

## Notes

- Actions are where work actually gets done
- Keep task descriptions concise but specific
- Mark items done as you complete them
- Update Log only when significant progress or blockers arise
- If action gets too large (>20 tasks), consider splitting into multiple actions

## Example

```yaml
---
id: A001
title: Signal Node Correctness — Post-Audit Items
status: IN_PROGRESS
design: D002
project: P001
created: 2026-05-30
updated: 2026-08-20
---

## Context

Phases 1–3 of signal-node-correctness action are complete (verified 2026-04-01). This action tracks remaining post-audit items and the pyramiding feature.

Full reference: `docs/signal-node-correctness-action.md`

## Tasks

### Post-Audit Fixes
- [ ] **Fix A**: DCASignalV2/V3 `shrink_to_fit()` anti-pattern
  - File: `nodegraph/dataio/NGDataIODCASignals.cpp`
  - Replace `mCtxBuf.assign(...) + shrink_to_fit()` with `std::fill`
  - Applies to both V2 and V3 reset blocks

- [ ] **Fix B**: BacktestMetrics missing `subBarSourceReal` field
  - File: `include/tradeflow/backtest/BacktestMetrics.h`
  - Add `bool subBarSourceReal = false;`
  - Print in Sub-Bar Stability output

- [ ] **Fix C**: Example schema uses DCASignalV2, needs V3
  - File: `data/schemas/strategy/test-stepped-scalper-01-xrpusd.json`
  - Change node TypeId 10218 → 10304 for node 15

### Pyramiding Feature
- [ ] **A**: DCALotManager.UpdateMostRecentOpenEntry(float stop, float target)
  - File: `source/appdata/DCALotManager.cpp`
  - Find most recent open entry, update stop/target in-place

- [ ] **B**: DCASignalV3.mLastEntryFired + IsPyramidAdd()
  - File: `nodegraph/dataio/NGDataIODCASignals.h`
  - Store mLastEntryFired (0/1/2); accessor returns >= 1.5f

- [ ] **C**: AutoTraderSys V3 entry dispatch
  - File: `systems/AutoTraderSys.cpp`
  - If IsPyramidAdd(): call UpdateMostRecentOpenEntry, log, no new order
  - If initial entry: PlacePercent as before

- [ ] **D**: Unit test DCASignalV3PyramidTest.cpp
  - File: `tests/DCASignalV3PyramidTest.cpp`
  - Test: shouldTrade 0→1 (entry), then 1→2 (step); assert entryFired=1 then 2

## Log

2026-08-20 — Action created. Phases 1–3 confirmed complete. Post-audit items and pyramiding remain.
```
