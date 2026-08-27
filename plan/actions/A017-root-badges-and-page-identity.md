---
id: A017
title: Root badges for all parentless items, page title/heading, reachable Save from Tree view
status: DONE
project: P009
created: 2026-08-27
updated: 2026-08-27
---

## Context

Drive-by follow-up from the same superplan-context session as A016.

## Tasks

- [x] Thesis-less master plans in the flat sidebar list got no badge at
      all (indistinguishable from "forgot to link"); added a "root"
      badge with a tooltip explaining it's intentional.
- [x] Extended root badges to projects with no `parent_master_plan`, and
      to actions — which surfaced a worse issue: an action naming a
      `project` but no `design` was never attached anywhere in
      `_build_hierarchy()`'s output and simply vanished from the tree.
      Fixed to attach such actions directly under their project; any
      action with neither a project nor a design now surfaces in a new
      "ACTIONS (no project/design)" section via a new `orphan_actions`
      key in `/api/hierarchy`, instead of disappearing.
- [x] `renderHierarchyView()` assumed every child of a project was a
      design (true only while designs were the only child type); now
      derives each child's type from its id prefix, and the section
      header ("Designs"/"Actions"/"Designs & Actions") reflects what's
      actually there.
- [x] Browser tab and toolbar showed a generic "Plan" with no way to
      tell which repo's plan was open. Added `detect_repo_name()`
      (parent-directory-name heuristic) and rendered it as "<repo> ·
      Plan" in the title plus a toolbar heading.
- [x] Tree view's "Full Doc" button called `FileBrowser.loadFile()`,
      which never restored `#file-toolbar` (hidden by
      `TreeView.showTree()`) — so there was no Edit button to reach from
      Tree view at all, and therefore no way to reach Save either.
      `loadFile()` now restores the toolbar regardless of which view
      called it.

## Log

2026-08-27 — Fixed across `src/planner/server.py`, `src/planner/static/{tree,files}.js`
(commits 41071a1, d91166d), logged retroactively per the new External
Contribution Workflow.
