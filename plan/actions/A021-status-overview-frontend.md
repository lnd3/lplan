---
id: A021
title: Frontend overview.js module + nav tab
status: IDEA
design: D004
project: P010
created: 2026-08-27
updated: 2026-08-27
---

## Context

Builds the UI half of D004: a new `overview.js` module rendering the rollup data from A020's endpoint, following the existing `analytics.js`/`status.js` class pattern (`init()`/`load()`/`render()`).

## Tasks

### Module
- [ ] `overview.js`: fetch `/api/status-overview`, render hierarchy rollups (progress bars per Master Plan / Project)
- [ ] Thesis/Concept health strip (status counts, no rollup)
- [ ] Wire into `dispatcher.js` and `nav.js`, new "Status" tab alongside Tree/Items/Analytics

### Interaction
- [ ] Row/bar click drills into existing entity view (reuse Items view's navigation pattern)

## Log

2026-08-27 — Action created, not started.
