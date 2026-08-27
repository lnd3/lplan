---
id: A019
title: Thesis<->master_plan content-pane display; toggle-glyph rotation cleanup; master plans get full sidebar + children view
status: DONE
project: P009
created: 2026-08-27
updated: 2026-08-27
---

## Context

Drive-by follow-up from the same superplan-context session as
A016-A018, working through a "rule of thumb: always show immediate
children of an item" pass across the whole Tree view.

## Tasks

- [x] Clicking a project always showed its Designs/Actions below the
      file content, but clicking a thesis showed nothing about its
      linked master plans at all (explicitly excluded from that logic),
      even though the sidebar nested them correctly. Generalized the
      content-pane child renderer via a new `TYPE_META` table keyed by
      id prefix (P/D/A/M/T) so the same renderer works for project->
      {design,action}, thesis->master_plan, and master_plan->thesis.
- [x] The thesis's own inline expand/collapse toggle (for its
      then-nested master-plan sub-list) never updated its own glyph —
      stuck on '+' forever, and wrong even on load (showed '+' despite
      starting expanded). Fixed to flip correctly via `this.textContent`.
- [x] Removed a `.tree-item:not(.collapsed) .tree-toggle { transform:
      rotate(90deg) }` CSS rule. It was a no-op before (rotating a
      static '+' 90deg doesn't change how it looks, which is why nobody
      noticed it) — but once the glyph was fixed to a real '-', that
      same rule rotated it into a vertical bar. Two conflicting
      mechanisms for the same state; the text flip alone is correct.
- [x] Sidebar "MASTER PLANS" only listed thesis-less plans (linked ones
      were nested under their thesis instead) — now lists every master
      plan, each badged with its thesis(es) or a root badge if it has
      none. Required removing the thesis-nested sidebar sub-list (would
      otherwise collide on DOM id with the comprehensive list); a
      thesis's master plans are still fully visible via its own content
      pane's "Master Plans" section instead.
- [x] A master plan's content pane now also shows a "Projects" section
      (projects whose `parent_master_plan` includes it), reusing the
      same recursive renderer a project uses for its own designs/
      actions — so a listed project that itself has children renders
      them too, recursively, per the "immediate children" rule.

## Log

2026-08-27 — Fixed in `src/planner/static/tree.js` (commits c6fd1cd,
42779f8), verified via headless-browser runs against both superplan's
and TradeFlow's real linked data (including the zero-children edge
case). Logged retroactively per the new External Contribution Workflow.
