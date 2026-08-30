---
id: A027
title: Validator — Parent-Child Status Consistency Check
status: IN_PROGRESS
priority: MEDIUM
priority_drivers:
  - quality_baseline
  - enables_multiple
created: 2026-08-30
updated: 2026-08-30
project: P001
design:
depends: []
external_dependencies: []
---

## Problem

A project (or design) can be marked DONE while its child designs or actions are
still IN_PROGRESS or BLOCKED. This goes undetected by the current validator and
produces misleading INDEX views. Real example: TradeFlow P005 was DONE while D007
was IN_PROGRESS and A006 was BLOCKED — the DONE entry was premature and stayed
wrong for ~9 days until a manual audit caught it.

Reverse case: a project can be BLOCKED while all its children finish — the parent
never gets promoted. TradeFlow P001 stayed BLOCKED for 9 days after its exchange
infrastructure dependency was resolved.

## Check Definition

**Warning (not error)**: emit a warning when:

1. **Parent DONE, child not terminal**: entity with `status == DONE` has at least
   one child entity whose status is not in `{DONE, DEFERRED, CANCELLED}`.
   - Parent = Project or Design
   - Child = Design where `design.project == parent.id`, or Action where `action.project == parent.id` or `action.design == parent.id`

2. **Parent BLOCKED, no child is BLOCKED**: entity with `status == BLOCKED` has
   no child and no `depends` entry that is itself BLOCKED or IN_PROGRESS. This
   catches stale BLOCKED parents after all blockers resolve. (Lower confidence —
   implement as optional / lower priority.)

Warnings, not errors, because legitimate partial-done states exist (e.g., a project
with one DEFERRED design that will never complete but the project is otherwise done).
The user decides whether to promote or annotate.

## Where

`deps/lplan/src/planner/validator.py` — `validate_relationships()` method.
Add after the existing project/design/action ref checks.

## Tasks

- [x] File A027, determine check definition
- [x] Implement check 1 (DONE parent with non-terminal child) in `validate_relationships()`
- [ ] Implement check 2 (BLOCKED parent with resolved children) — lower priority
- [ ] Add test cases to lplan test suite
- [ ] Update QUICK_REFERENCE.md to document the new warning

## Log

2026-08-30 — Filed from TradeFlow context: P005 DONE+D007 IN_PROGRESS+A006 BLOCKED,
  and P001 BLOCKED after its blocker resolved, both went undetected for ~9 days.
  Check 1 implemented immediately. Check 2 deferred.
