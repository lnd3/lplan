---
id: A033
title: Rename Internal View Naming to Match Toolbar Buttons
status: DONE
design: D004
project: P010
created: 2026-08-30
updated: 2026-08-30
---

## Context

User feedback, prompted directly by an ambiguity that came up earlier this session: the code's internal naming didn't match the toolbar button labels the user actually refers to views by. `status.js`'s class was `StatusView`, but its button is "📋 Items" — and `overview.js`'s class was `OverviewView`, but its button is literally "🩺 Status". This is exactly why an earlier request ("sort projects in Status view") was ambiguous between two different views.

## Tasks

- [x] `overview.js`/`OverviewView` → `status.js`/`StatusView` (button: "🩺 Status")
- [x] old `status.js`/`StatusView` → `items.js`/`ItemsView` (button: "📋 Items")
- [x] DOM container ids swapped to match: `#overview-view` → `#status-view`, old `#status-view` → `#items-view`
- [x] `data-action` strings swapped: `show-overview` → `show-status`, old `show-status` → `show-items`
- [x] `dispatcher.js` updated to match
- [x] Sibling views that hide both containers when switching tabs (`analytics.js`, `files.js`, `tree.js`) updated to the new ids
- [x] `<script src>` tags in `server.py` swapped to load `items.js` then `status.js`
- [x] Design docs (D004, D007) that described the old filenames as current architecture updated; historical Log entries elsewhere (P010, D004 itself, other actions) left untouched — they correctly describe what the file was called at the time
- [x] Verified live via jsdom against a running server: both tabs still show/hide the correct container, Items view still renders real rows, Status dashboard still renders rollup content, a third tab (Tree) still hides both correctly, and `window.OverviewView` no longer exists while `window.ItemsView`/`window.StatusView` do

## Log

2026-08-30 — Implemented as a careful ordered swap (not a naive find-replace — "status-view" and "overview-view" both needed to become each other's opposite value across 6 files, which requires converting one before creating instances of it via the other). 119/119 tests pass (Python side untouched — this was purely a JS/HTML rename). All wiring re-verified live via jsdom, not just `node --check`.
