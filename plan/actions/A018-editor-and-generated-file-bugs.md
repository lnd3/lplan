---
id: A018
title: Save/Cancel never visible in edit mode; sidebar toggle glyph stuck; INDEX.md wrongly editable
status: DONE
project: P009
created: 2026-08-27
updated: 2026-08-27
---

## Context

Drive-by follow-up from the same superplan-context session as A016/A017,
found while the user tried to actually use editing after the Tree-view
Save-button-reachability fix in A017 landed.

## Tasks

- [x] `#btn-save`/`#btn-cancel` have `display: none` baked into their
      base CSS rule. `enterEdit()` "revealed" them by clearing the
      inline style override (`style.display = ''`), which doesn't set a
      visible value — it just falls back to that stylesheet rule, so
      both buttons stayed hidden every time edit mode was entered, in
      any view. Fixed by setting an explicit `inline-block`. Confirmed
      via `getComputedStyle`, not just the inline attribute, and via a
      scripted end-to-end save that changed a real file on disk.
- [x] The sidebar's `+`/`-` expand toggle never updated its own glyph or
      collapsed-state CSS class — the click listener is delegated to
      `document`, so `event.currentTarget` inside `toggleTreeItem` was
      always `document`, never the clicked `.tree-toggle` span. The
      actual expand/collapse worked underneath (doesn't depend on that
      variable), but with zero visual feedback it looked broken. Fixed
      to use `event.target` and an explicit collapsed-state boolean
      instead of a bare `classList.toggle()` flip.
- [x] `INDEX.md` is unconditionally rebuilt by
      `_auto_regenerate_index()` on every view — hand-editing it looked
      successful (banner, preview update) but silently vanished the next
      time it was viewed. Rather than fix persistence for a fundamentally
      derived file, stopped offering Edit on it at all (in both
      `enterEdit()` and `cancelEdit()`), plus an inline note explaining
      why in the path bar.
- [x] `detect_repo_name()` now prefers README.md's first `#` heading
      (the stable, human-maintained ground truth for a repo's identity)
      over the directory-name guess, with the guess remaining as a
      last-resort fallback and an explicit `.plan-config` override still
      taking precedence over both.

## Log

2026-08-27 — Fixed across `src/planner/static/editor.js`,
`src/planner/static/tree.js`, `src/planner/index_gen.py`, `src/planner/static/preview.js`
(commits b980968, a2e70d4, 23fbc9e, 493dbce), logged retroactively per
the new External Contribution Workflow.
