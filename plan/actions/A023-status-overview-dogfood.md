---
id: A023
title: Dogfood against lplan's own plan/
status: IN_PROGRESS
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

Validate the finished dashboard against lplan's own `plan/` directory as a real test case, since it already has known edge cases worth checking: A015 (should show stale), P009 (perpetual catch-all — should not be flagged as unusually stagnant even though it never reaches DONE), and the A008/A011/A015 orphaned-reference / P009 unused-project findings from `check-refs`.

## Tasks

- [x] Confirm A015 appears in the stale-work panel — confirmed at the API level (flagged at 3 days idle, along with P007 and M001 which are also stale by the same measure — a useful surprise, see below)
- [x] Confirm P009 is not misrepresented by the rollup math — confirmed: shows 100% (4/4 actions DONE), which is correct and not "broken looking" even though P009 itself stays IN_PROGRESS forever by design
- [x] Confirm dangling-reference panel matches `plan check-refs` output exactly — confirmed byte-for-byte (A008/A011/A015 orphaned, P009 unused)
- [x] Confirm Master Plan rollups render sensibly — confirmed at the time against M001 (57%, 4/7) and a second master plan with a different fill level (50%, 1/2); that second one (M002) was later moved to the accessibility-lplan repo, 2026-08-30, so the specific numbers are no longer reproducible here
- [ ] Visual/click-through confirmation in an actual browser — **not done**, this sandbox has no headless browser available. Everything above was confirmed via a standalone Python script and via curl against a running `plan serve` instance, not by looking at the rendered page.

## Log

2026-08-27 — Ran the dogfood checks at the data level (API responses), all four planned checks passed. One unplanned finding: staleness surfaced M001 and P007 as stale too, not just A015 — expected, since they share the same 2026-08-24 last-activity date, and it's a reasonable demonstration that the panel catches drift beyond the single case it was scoped around. Left IN_PROGRESS rather than DONE because the visual/browser leg of dogfooding is still open — recommend the user run `plan serve` and click "🩺 Status" to close this out.
2026-08-27 — Action created, not started.
