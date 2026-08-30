---
id: A033
title: Skip phase-anchor warnings on terminal-status projects
status: DONE
priority: LOW
project: P009
created: 2026-08-30
updated: 2026-08-30
---

## What

`validate_phase_anchors()` was emitting warnings for every unanchored phase in projects
with status DONE, DEFERRED, or CANCELLED. These are closed projects — their phase gaps
are historical, not actionable. In TradeFlow, P009 (3 phases) and P002 Phase 6 were
generating 4 noise warnings that obscured the real gaps.

## Fix

Added a terminal-status guard at the top of the per-project loop in `validator.py`:

```python
terminal = {Status.DONE, Status.DEFERRED, Status.CANCELLED}
if project_entity and project_entity.status in terminal:
    continue
```

## Log

2026-08-30 — DONE. Drive-by fix from TradeFlow session. Reduced TradeFlow validate warnings from 14 to 10.
