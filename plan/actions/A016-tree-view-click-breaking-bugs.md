---
id: A016
title: Fix tree-view clicks breaking on apostrophes and duplicate master-plan DOM ids
status: DONE
project: P009
created: 2026-08-27
updated: 2026-08-27
---

## Context

Drive-by fix made from superplan's context (a hub repo consuming lplan
as a submodule) while browsing its own new theses/master-plan/project
items in the web UI's Tree view. Not planned in advance — discovered by
using the tool.

## Tasks

- [x] `onclick='TreeView.showTreeRoot(...)'` interpolated titles raw into
      a single-quoted HTML attribute; a title containing an apostrophe
      (e.g. "TradeFlow's ...") silently truncated the attribute and broke
      that node's click handler. Added `TreeView.escapeAttr()` (HTML
      entity encoding) and applied it at every `showTreeRoot()` call site.
- [x] `highlightTreeItem(id)` looked up `#tree-${id}`, but master-plan
      nodes used `tree-mp-${id}` / `tree-${thesisId}-${id}` — neither
      matched, so master plans never got the active/selected highlight.
      Normalized both to `tree-${id}`.
- [x] The flat "MASTER PLANS" list computed an `unlinkedMPs` filter but
      then iterated over the unfiltered list anyway, so thesis-linked
      master plans rendered twice with conflicting duplicate DOM ids.
      Fixed to actually use the filter.

## Log

2026-08-27 — Fixed in `src/planner/static/tree.js` (commit 3f882af),
logged retroactively per the new External Contribution Workflow.
