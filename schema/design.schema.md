# Design File Schema

A design file documents architectural decisions, specifications, and implementation details.

## Location & Naming
- Location: `plan/designs/`
- Naming: `D<NNN>-kebab-case-title.md`
- Examples: `D001-anchored-levels.md`, `D002-signal-node-correctness.md`

## Required Frontmatter Fields
- `id`: D001, D002, etc.
- `title`: Design title
- `status`: IDEA, PLANNING, IN_PROGRESS, DONE, DEFERRED, CANCELLED (no BLOCKED for designs)
- `project`: Parent project ID (e.g., P001)
- `created`: YYYY-MM-DD
- `updated`: YYYY-MM-DD

## Optional Frontmatter Fields
- `depends`: List of "repo:ID" designs/projects this depends on
- `external_dependencies`: List of external features needed
- `description`: One-line summary
- `doc_link`: Path to full design doc in repo (if design is extensive)

## Content Sections

### ## Summary
1 paragraph: What problem does this design solve? What approach does it take?

### ## Architecture
High-level structure, components, and how they interact.

### ## Implementation Status
- [ ] Phase 1: Description
- [ ] Phase 2: Description
- [x] Phase 3: Description (if in progress)

### ## Key Decisions
List of important design choices and their rationale:
- **Decision 1**: Why we chose X over Y (tradeoff: Z)
- **Decision 2**: Why we chose A over B (tradeoff: C)

### ## Open Questions / Unknowns
What's not yet settled, and how it will be resolved.

### ## Related
Links to:
- Full design document (if in docs/)
- Related projects/designs/actions
- Reference materials

### ## Log
Append-only changes to the design.

## Notes

- Designs document *what to build*, not how to build it (that's actions)
- Keep designs in `plan/designs/` as summaries; full specs go in `docs/` or elsewhere
- Link to full docs via `doc_link` or Related section
- Designs are typically DONE when specification is complete (implementation status tracked in actions)

## Example

```yaml
---
id: D001
title: Anchored Volume Levels V3
status: DONE
project: P001
created: 2026-05-30
updated: 2026-08-20
doc_link: "docs/anchored_levels_design.md"
---

## Summary
Design for volume-anchored price level detection with regime-based snapshots. Replaces rolling accumulation approach with segmented anchoring to reduce noise and improve level stability.

## Architecture
- **AnchoredLevelTracker** (header-only model): Maintains state machine for accumulation/confirmation/output phases
- **VolumeLevelsV3 node**: Wraps tracker, processes OHLCV data, outputs levels + segment transitions
- **Visualization**: SegmentBoundaryViz shows transitions in MarketGraph

## Implementation Status
- [x] Phase 1: Core state machine (AccumulatingState → ConfirmingState → OutputState)
- [x] Phase 2: Deterministic rewind detection (via bar timestamps)
- [x] Phase 3: Viz node (SegmentBoundaryViz, type=9)
- [ ] Phase 4: Unit tests (comprehensive coverage)

## Key Decisions
- **Segmentation over rolling**: Reduces noise from bar-by-bar drift; snapshot only on confirmed segments (tradeoff: requires segment confirmation delay)
- **Timestamp-based rewind**: Detects data prepend via barTime change, not manual flags (tradeoff: assumes monotonic time in data)
- **Type=9 for viz**: Vertical lines at segment boundaries (tradeoff: new render type adds complexity, but provides clear visual indication)

## Open Questions
- Min/max segment bar length tuning (currently 10–30 bars)
- Bounce rate calculation for regime filtering (currently 0.5, uninformed)

## Related
- Full design: `docs/anchored_levels_design.md`
- Action: A003 (VolumeLevels V3 Remaining)
- Project: P001 (Price Levels Strategy)

## Log
2026-08-20 — Design finalized. Implementation (phases 1–3) complete. Phase 4 (tests) pending.
2026-05-30 — Design created and approved.
```
