---
id: A021
title: Frontend overview.js module + nav tab
status: DONE
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

Builds the UI half of D004: a new `overview.js` module rendering the rollup data from A020's endpoint, following the existing `analytics.js`/`status.js` class pattern (`init()`/`load()`/`render()`).

## Tasks

### Module
- [x] `overview.js`: fetch `/api/status-overview`, render hierarchy rollups (progress bars per Master Plan / Project)
- [x] Thesis/Concept health strip (as per-type totals cards showing status counts — folded into the summary row rather than a separate strip; no rollup, matches D004's "flat counts only" decision)
- [x] Wire into `dispatcher.js` (there's no separate `nav.js` — toolbar wiring lives in `server.py`'s HTML + `dispatcher.js`, same as Items/Analytics), new "🩺 Status" tab alongside Files/Tree/Analytics/Items

### Interaction
- [x] Row/bar click drills into existing entity view (`EntityViewer.show`, same call Items view uses)

## Log

2026-08-27 — Second bug found via browser use: Projects section got cut off at the bottom with no way to reach the rest. Cause: `#overview-view` never got the `overflow-y: auto` CSS rule that `#tree-view`/`#analytics-dashboard` have in style.css — that's what lets a flex child (inside `#content`'s `display:flex; flex-direction:column`) shrink to available space and actually scroll. The inline `overflow-y:auto` on `overview.js`'s inner wrapper div didn't help, since the outer flex item itself stayed unbounded. Fixed by adding `#overview-view { padding: 20px; overflow-y: auto; }` to style.css (matching the sibling views) and dropping the redundant inline wrapper. Also added collapsible sections (Needs Attention, Master Plans, Projects) via a reusable `renderCollapsible()` helper, click-to-toggle header, state kept in a session-local `Set` — addresses "or collapsible" from the request directly, not just scrolling.
2026-08-27 — Bug found via actual browser use (by the user, not this sandbox): row/bar clicks didn't navigate. Cause: `/api/status-overview` never returned a `path` field, so `overview.js` guessed `${dir}/${id}.md`, which doesn't match real filenames like `P001-tier1-engine.md`. Fixed by threading a `path_by_id` map (same one `/api/status` already builds) through `status_overview.py` into every rollup/needs-attention entry, and having `overview.js` use `entity.path` instead of guessing. Verified the fix via curl: `/api/status-overview` now returns real paths, and `/api/file?path=...` (what `EntityViewer` fetches) resolves them with 200s. This is exactly the class of bug D004 flagged as a risk of not having a headless browser available — confirms it needed a real look.
2026-08-27 — Built `overview.js` following the `analytics.js`/`status.js` class pattern. Verified via `node --check` (syntax) and via curl against a running `plan serve` that the button, container, and script tag are present in the served HTML. **Caveat**: this sandbox has no headless browser available, so actual rendering/layout/click-through was not visually verified — only the data layer (API responses) and static wiring were confirmed. Recommend a manual check in a real browser before considering this fully done.
2026-08-27 — Action created, not started.
