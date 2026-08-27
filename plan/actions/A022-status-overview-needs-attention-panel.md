---
id: A022
title: Needs-attention panel (stale, blocked, dangling refs)
status: DONE
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

The surfacing half of D004 — turning A020's staleness/blocked/dangling-ref signals into a visible panel, rather than data the user has to know to go look for. This is the part that actually addresses the original complaint (FOCUS.md and A015 drifting stale for days with nothing pointing it out).

## Tasks

- [x] Panel listing stale IN_PROGRESS entities with days-since-activity
- [x] Panel section for BLOCKED entities with their blocker(s)
- [x] Panel section for dangling references (orphaned/unused entities per `check-refs`)
- [x] Empty-state handling: each sub-section only renders if it has content; if all three are empty, one "✓ nothing needs attention" message shows instead of an empty panel

## Log

2026-08-27 — Built as part of `overview.js` (`renderNeedsAttention`). Confirmed via the live API (not the rendered DOM — see A021's caveat) that stale/blocked/dangling-ref data is correctly assembled and would populate each section as designed.
2026-08-27 — Action created, not started.
