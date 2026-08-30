---
id: D008
title: Project Phase → Design/Action Linking (Loose Coupling)
status: IN_PROGRESS
priority: MEDIUM
project: P001
created: 2026-08-30
updated: 2026-08-30
---

## What

A loose coupling between project phases and child Designs/Actions. Each phase in
a project file is a human-authored planning section — free-form text, checkboxes,
notes — that may reference one or more Designs as structural anchors. Actions are
optional and may be missing, incomplete, or not yet created. Checkboxes within a
phase do not need to map to files.

**Single structural rule**: every phase must have at least one Design. The Design
documents the *what* and *why* of the phase. Everything else (tasks, Actions,
notes, open questions) is free-form.

## Why

The original D008 draft proposed tight coupling: every task maps to an Action,
and the project file's `## Phases` section becomes a generated artifact. This is
too rigid in practice:

- Phases hold high-level context that predates any Action being written.
- A phase may have gaps — missing designs, incomplete actions, future work not
  yet decomposed.
- Not every checkbox corresponds to a discrete Action; some are notes, steps, or
  research items that don't warrant a file.
- The project file is a planning document, not a derived artifact. It should remain
  authoritative for phase intent even when the implementation is incomplete.

The looser model preserves the project file as a planning surface while adding
enough structure to keep phases grounded and visible in the rollup.

## How

### `phase` field on Designs (required anchor) and Actions (optional)

```yaml
# Design — required anchor for the phase
id: D001
project: P001
phase: "Phase 1 — Strategy Pipeline"

# Action — optional; links into the same phase
id: A013
project: P001
phase: "Phase 3 — V3 Tuning, Real Data Validation, Cleanup"
```

### Project file — phases remain human-authored

The `## Phases` section in the project file is **not generated**. It is the
source of truth for phase names and phase-level intent. Checkboxes are free-form;
they may or may not correspond to Action files.

```markdown
## Phases

### Phase 1 — Strategy Pipeline [D001 DONE, A001 DONE, A003 DONE]
- [x] VolumeLevels V3, HTFRegimeDetector, MultiTFFilter, PositionSizerV2, DCASignalV3
- [x] TradingSizerStepped1 + viz

### Phase 3 — V3 Tuning [D001 DONE, A013 IN_PROGRESS]
- [ ] Sweep minStrength / minSegBars / confirmBars across assets
- [ ] Real data validation on live XRP/USD
- [ ] Lock params; save regression baseline
- (no action for: document tuning methodology) ← gap, fine
```

The bracketed `[D001 DONE, A013 IN_PROGRESS]` is the human-maintained
phase header annotation. The validator checks that at least one of those
references is a Design.

### Validator rule (warn, not error)

`validate_relationships()` adds:

```
For each project:
  parse ## Phases section, extract phase headers
  for each phase header:
    collect bracketed entity refs [D001, A013, ...]
    warn if none of the refs resolves to a Design entity
```

This is a soft check — warns only, never blocks. Phases without any Design ref
are flagged as "unanchored" in the validation report.

### `generate-index` — optional phase summary table

If at least one child has a `phase` field, `generate-index` emits a supplementary
phase table below the project's `## Linked` section:

```markdown
## Phase summary (from children)

| Phase | Designs | Actions | Status |
|---|---|---|---|
| Phase 1 — Strategy Pipeline | D001 | A001, A003 | DONE |
| Phase 2 — Backtest Validation | — | A012 | DONE |
| Phase 3 — V3 Tuning | D001 | A013 | IN_PROGRESS |
| Phase 4 — Live Deployment | D007 | — | BLOCKED |
```

Status = worst-case child status for that phase. "—" for missing designs or
actions is valid and expected.

### Checkbox extraction (optional, later)

`generate-index` can count `- [ ]` / `- [x]` per Action/Design file and include
completion percentages in the phase table. This makes in-file task completion
visible without requiring every checkbox to have a file backing it.

## Constraints

- `phase` is optional on all entities. Existing schemas with no `phase` fields
  are unaffected.
- Phase names are free-form strings. The validator matches refs in brackets
  against known entity IDs — it does not parse or validate phase names.
- A phase may reference a Design that is DONE (completed phases are fine).
  The validator only checks *presence* of a Design ref, not its status.
- Phases without a `## Phases` section are valid projects — the feature is opt-in.
- The project file's phase text, checkboxes, and notes remain
  human-maintained. Only the bracketed entity refs `[D001, A013]` are
  machine-readable.

## Implementation Phases

- [x] **Phase 1**: Add `phase` field to Design/Action Pydantic models (optional str) — `models.py`, wired through `parser.py`'s `_parse_design`/`_parse_action`
- [x] **Phase 2**: Validator warns on unanchored phases (no Design ref in brackets) — new `SchemaValidator.validate_phase_anchors()`, parses a project file's `## Phases` section directly (needs raw markdown, so it's a separate method from `validate_relationships()`, not folded into it); wired into `plan validate`
- [x] **Phase 3**: `generate-index` emits phase summary table from child `phase` fields — new `## Phase Summaries` section, one sub-table per project with any `phase`-tagged children, worst-case status per phase (BLOCKED worst, DONE best); an Action resolves its project via its own `project` field or, if unset, its parent Design's `project`
- [ ] **Phase 4**: Checkbox extraction — open task count per Action/Design in phase table. Not started; explicitly lower priority per this design's own framing ("optional, later")

## Log

2026-08-30 — Implementation started at user request; Phases 1–3 done (see A028). Phase 4 (checkbox extraction) left for later, as this design itself already deprioritizes it.
2026-08-30 — Initial draft proposed tight coupling (every task → Action, project
  phases generated from children). Revised: loose coupling after user feedback.
  Phase text is human-authored and may have gaps; Design is the minimum anchor per
  phase; Actions are optional. Validator warns on unanchored phases (no Design ref).
  Project file remains authoritative for phase intent.
