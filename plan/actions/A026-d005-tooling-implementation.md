---
id: A026
title: D005 Tooling Implementation — Companion File Support
status: DONE
design: D005
project: P008
created: 2026-08-30
updated: 2026-08-30
---

## Context

Implements D005's "How" section: tooling support for the companion-file convention (`{root}_{suffix}.md`), plus the template comment blocks that make it discoverable.

## Tasks

### Detection
- [x] New `src/planner/companions.py`: `is_companion_file()` (any `.md` stem containing `_`), `companion_suffix()`, `companion_root_stem()`, `find_companions()`

### `plan validate`
- [x] `PlanParser.parse_directory()` skips companion files before attempting to parse them as entities — previously any non-frontmatter `.md` dropped into an entity subdirectory (e.g. a future `D005_learnings.md`) showed up as a hard "files had parse errors" failure

### `plan generate-index`
- [x] `write_index()`/`generate_index()`: companions excluded from entity tables (they're not entities), surfaced instead as a "📎 see also" note on their root entity's row
- [x] `--include-companions` flag appends a trailing "## Companions" inventory table

### `plan check-refs`
- [x] New `check_companion_links()` in `refs.py`: scans root/entity `.md` files for markdown links to companion-looking targets (stem contains `_`) and flags ones that don't resolve, as `dead_companion_links` in the report
- [x] Guards against false positives from illustrative links inside fenced code blocks and inline code spans (both found and fixed during dogfooding — see D005_learnings.md)
- [x] Wired into CLI output and into `status_overview.py`'s `dangling_references()` so P010's dashboard surfaces dead companion links too

### Template comment blocks
- [x] Added to `action`, `concept`, `master_plan`, `project`, `thesis` templates (design.md.template already had one)
- [x] Added to `CHANGELOG.md.template`, `WORKFLOW.md.template`, `AXIOMS.md.template` (the root templates D005 explicitly named)
- [x] `FOCUS.md.template`/`REFLECTION.md.template` already communicated the convention (predates this action) — left as-is

### Dogfood
- [x] Reformatted this repo's own `plan/REFLECTION.md` back to its template's one-liner format (it had drifted into markdown sections — the exact failure D005 exists to prevent), moving detail to new `plan/REFLECTION_extension.md`
- [x] Split `plan/FOCUS.md` overflow into new `plan/FOCUS_context.md`
- [x] Created `plan/designs/D005_learnings.md` as a real entity-level companion, verifying the full path: parses without error, shows as "see also" in INDEX.md, appears in `--include-companions` output

## Log

2026-08-30 — Implemented and dogfooded per the checklist above. 100/100 existing tests still pass throughout; `plan validate`/`check-refs`/`generate-index` all verified against this repo's own plan/ at each step, not just at the end.
