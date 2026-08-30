---
id: A015
title: Implement SVG dependency graph visualization
status: IN_PROGRESS
created: 2026-08-23
updated: 2026-08-30
description: Create SVG renderer for project dependencies with status-based colors and phase-based layout.
design: D007
project: P007
priority: MEDIUM
---

## Goal

Build the SVG visualization engine that renders project dependencies as an interactive directed graph. Projects are laid out by execution phase (columns), with edges showing dependencies.

## Scope

- Phase-based layout engine (X-axis = phases, Y-axis = projects within phase)
- SVG path rendering for dependency edges
- Status-based colors (DONE=green, IN_PROGRESS=blue, BLOCKED=red, etc.)
- Interactive elements (hover tooltips, click-to-navigate)
- Responsive sizing to fit container

## Tasks

- [x] Implement phase-based coordinate calculation
- [x] Create SVG path generator for edges
- [x] Add status color mapping
- [x] Build node rendering with labels
- [ ] Add interactive hover effects / click-to-navigate
- [ ] Test with sample project graphs (no dedicated test exists — see D007's Testability)

## Log

2026-08-30 — Found while aligning P007 with current state: this action's stalled status/log was misleading. The described work is actually done — `report.py`'s `_generate_dependency_graph_svg()` (built under the P003/Tier-3 push, not tracked back to this action at the time) implements phase-based coordinates, SVG edges with arrowheads, status-color-coded nodes, and labels. Verified by regenerating `plan report` against this repo's current plan/ and confirming real `<svg>`/`<rect class="node">` output. Retroactively documented in new D007 (this action's `design:` field had been pointing at a design doc that never existed — `plan check-refs` had been flagging this as an orphan the whole time).
2026-08-30 — What's genuinely still open: it's a *static-report-only* renderer — never wired into the live "📊 Analytics" dashboard (which shows Gantt + burndown instead), so there's no live interactivity to add hover/click-to-navigate to yet. Left IN_PROGRESS rather than DONE for that reason, but the remaining scope is now accurately "wire into the live dashboard + add interactivity + add a test," not "build the renderer" — see D007's Open Questions for the unresolved scope call (live-dashboard integration vs. leaving it static-report-only).
2026-08-24 — SVG path generator complete. Node rendering in progress.
2026-08-23 — Task started. Layout algorithm designed.
