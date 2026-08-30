---
id: A023
title: Dogfood against lplan's own plan/
status: DONE
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
- [x] Click-through confirmation via a real DOM environment — no headless browser was ever available in this sandbox, so used `jsdom` instead: fetched the live page from a running `plan serve`, executed all client-side scripts for real inside a DOM (`runScripts: "dangerously"`, a `window.fetch` shim resolving relative URLs against the server), then dispatched genuine `click` events through the actual listeners. 21/21 checks passed: toolbar tab-switching hides/shows the right containers, the dashboard renders real content (totals, needs-attention, both rollup sections, P010's own row), the collapsible-section toggle actually flips `.collapsed` and the glyph, clicking a project row fires `EntityViewer.show` and loads real content via `/api/file`, and `#overview-view`'s `overflow-y:auto` CSS rule is confirmed present (the scrolling fix from A021 is live). This is DOM-execution verification, not a pixel-level screenshot — but it exercises the real rendering and event-handling code end-to-end, which is what the outstanding checklist item was actually asking for.

## Log

2026-08-30 — Closed the last checklist item via jsdom-based DOM execution against a live `plan serve` instance (script kept at `/tmp/lplan-scratch/jsdom-test/verify_overview.js` for this session only, not committed — scratch tooling, not part of the repo). All 21 checks passed. A023 and P010 now DONE.
2026-08-27 — Ran the dogfood checks at the data level (API responses), all four planned checks passed. One unplanned finding: staleness surfaced M001 and P007 as stale too, not just A015 — expected, since they share the same 2026-08-24 last-activity date, and it's a reasonable demonstration that the panel catches drift beyond the single case it was scoped around. Left IN_PROGRESS rather than DONE because the visual/browser leg of dogfooding is still open — recommend the user run `plan serve` and click "🩺 Status" to close this out.
2026-08-27 — Action created, not started.
