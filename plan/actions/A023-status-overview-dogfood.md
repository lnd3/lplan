---
id: A023
title: Dogfood against lplan's own plan/
status: IDEA
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

Validate the finished dashboard against lplan's own `plan/` directory as a real test case, since it already has known edge cases worth checking: A015 (should show stale), P009 (perpetual catch-all — should not be flagged as unusually stagnant even though it never reaches DONE), and the A008/A011/A015 orphaned-reference / P009 unused-project findings from `check-refs`.

## Tasks

- [ ] Confirm A015 appears in the stale-work panel
- [ ] Confirm P009 is not misrepresented by the rollup math (0 children ever expected is fine; it shouldn't read as broken)
- [ ] Confirm dangling-reference panel matches `plan check-refs` output exactly
- [ ] Confirm Master Plan rollups (M001, M002) render sensibly given M001 has real IN_PROGRESS/DONE projects and M002 has none yet

## Log

2026-08-27 — Action created, not started.
