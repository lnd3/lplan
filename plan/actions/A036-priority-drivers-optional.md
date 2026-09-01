---
id: A036
title: Priority Drivers — Optional at Parse, Enforced by Validator
status: DONE
priority: LOW
project: P009
created: 2026-09-01
updated: 2026-09-01
---

## What was done

Commit `68d3796` (drive-by from TradeFlow) made `Project.priority_drivers` optional at the model level (`default_factory=list`, no longer a required+non-empty Pydantic field) and removed the field-level `@field_validator` that enforced non-emptiness — omitting the field previously raised a parse error that silently dropped the whole entity from every view (Tree, Status, Items).

That commit's message said "no validator needed," but `SchemaValidator._validate_project` (`src/planner/validator.py`) already had its own independent "must not be empty" check, so the field was never actually left unenforced — it just moved from a hard parse-time crash to a soft validation error surfaced in the Status dashboard. Follow-up work in this Action:

- Filed this Action + updated `plan/CHANGELOG.md`'s existing line — the original commit logged a CHANGELOG entry under P009 but never filed the accompanying Action WORKFLOW.md requires for a drive-by bug fix.
- Added driver-key validation to `SchemaValidator._validate_project`: when `priority_drivers` is non-empty, each entry must match `PriorityEngine`'s known driver keys or the `deferred_wait_*` pattern — previously unknown drivers were silently ignored by the scoring engine with no validation anywhere.
- Fixed two stale tests (`test_models.py::test_empty_priority_drivers_fails`, `test_validator.py::test_validate_project_empty_drivers`) that still asserted the old model-level `ValueError` behavior; added tests for the new unknown-driver check and the `deferred_wait_*` allowance.
- Updated `schema/frontmatter.md` and `schema/project.schema.md`, which still documented `priority_drivers` as required — now documented as optional-at-parse, required-and-validated by `plan validate`.

## Why

User's explicit intent (asked directly): the field should be optional so a missing value can't crash parsing and vanish the entity, but omitting or emptying it must still be caught — by the validator, not the parser — and any value that is present must be checked against the real driver vocabulary, not silently accepted.

## Log

2026-09-01 — Filed retroactively to close the gap: 68d3796 landed without an Action. Added driver-key validation, fixed stale tests, updated schema docs.
