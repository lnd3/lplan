---
id: A028
title: D008 Implementation — Phases 1–3
status: DONE
design: D008
project: P001
created: 2026-08-30
updated: 2026-08-30
---

## Context

Implements D008's Phases 1–3 at user request: the `phase` field on Design/Action, the validator's unanchored-phase warning, and `generate-index`'s phase summary table. Phase 4 (checkbox extraction) is out of scope here — D008 itself already marks it "optional, later."

## Tasks

### Phase 1 — `phase` field on entities
- [x] Add `phase: Optional[str] = None` to `Design` and `Action` in `models.py`
- [x] Wire it through `parser.py`'s `_parse_design`/`_parse_action`

### Phase 2 — Validator: unanchored phase warning
- [x] New `SchemaValidator.validate_phase_anchors()` — parses a project's raw `## Phases` section (needs markdown body, not just parsed entities, so it's a separate method rather than folded into `validate_relationships()`)
- [x] Extracts `### <name> [<refs>]` headers, checks at least one bracketed ref resolves to a `Design`
- [x] Wired into `plan validate` (reads `PlanFile.raw_content` for each Project)
- [x] 4 test cases: no `## Phases` section (silent), anchored phase (silent), no refs at all (warns), refs present but none is a Design (warns)

### Phase 3 — `generate-index` phase summary table
- [x] New `## Phase Summaries` section, one sub-table per project with any `phase`-tagged children
- [x] Groups by (project, phase name); an Action without its own `project` resolves via its parent Design's `project`
- [x] "Worst-case status" per phase (BLOCKED worst, DONE best) via a severity ordering
- [x] 2 test cases: no phase data anywhere (section absent), grouping + cross-Design project resolution (present, correct)

## Log

2026-08-30 — Implemented and tested. 110/110 tests pass (100 pre-existing + 4 A027 tests + 4 phase-anchor tests + 2 phase-summary tests). Verified against lplan's own `plan/` — no false positives, since nothing here uses the `## Phases`/`phase` convention yet (correctly silent, opt-in). Not yet dogfooded with a real project migrated to the new convention — that's a content migration, not a code task, left for whenever a project actually wants it.
