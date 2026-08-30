---
id: A029
title: Surface Validator Warnings in the Status Dashboard
status: DONE
design: D004
project: P010
created: 2026-08-30
updated: 2026-08-30
---

## Context

User asked to review the Status Overview dashboard "for incorrect assumptions" after A027/D008 landed. Found one: the needs-attention panel's `dangling_references()` only ever called `refs.check_references()` — it never ran the full `SchemaValidator`, so A027's new parent-child status warning and D008's new unanchored-phase warning were both invisible in the live dashboard, even though `plan validate` showed them from the moment A027 landed. The dashboard's implicit assumption when it was built (P010, 2026-08-27) was that check-refs was the complete universe of "things worth flagging" — true then, no longer true once the validator grew new warning types.

## Tasks

- [x] New `status_overview.collect_validator_warnings()`: runs `SchemaValidator.validate_entity()` + `validate_relationships()` + `validate_phase_anchors()` over the full entity set, same code path `plan validate` uses
- [x] Wired into `compute_status_overview()`'s `needs_attention` payload as `validator_warnings`, each entry carrying `id`/`type`/`field`/`message`/`path` (path threaded through for click-to-navigate, matching every other needs-attention entry)
- [x] `overview.js`: new "⚠ Validator warnings" section in the needs-attention panel, clickable like the rest
- [x] Verified live: confirmed via jsdom DOM execution against a running `plan serve` that the section renders with real warning text (not just checked via curl)
- [x] New `tests/test_status_overview.py` (this module had zero test coverage before) — 4 tests: A027-style warning surfaces with correct type, a clean plan stays silent, D008-style unanchored-phase warning surfaces, path threads through correctly

## Log

2026-08-30 — Implemented and verified. 114/114 tests pass (110 + 4 new). Confirmed against lplan's own plan/: the dashboard now shows both real warnings that already existed (`A011`'s orphaned design ref, pre-existing) and the new one A027 just found (`D007` DONE with non-terminal child `A015`) — previously invisible outside the CLI.
