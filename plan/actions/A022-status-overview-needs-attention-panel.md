---
id: A022
title: Needs-attention panel (stale, blocked, dangling refs)
status: IDEA
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

The surfacing half of D004 — turning A020's staleness/blocked/dangling-ref signals into a visible panel, rather than data the user has to know to go look for. This is the part that actually addresses the original complaint (FOCUS.md and A015 drifting stale for days with nothing pointing it out).

## Tasks

- [ ] Panel listing stale IN_PROGRESS entities with days-since-activity
- [ ] Panel section for BLOCKED entities with their blocker(s)
- [ ] Panel section for dangling references (orphaned/unused entities per `check-refs`)
- [ ] Empty-state handling: panel collapses/hides sections with nothing to report, doesn't show three "all clear" messages by default

## Log

2026-08-27 — Action created, not started.
