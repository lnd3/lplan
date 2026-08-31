---
id: A035
title: Validator — Duplicate Entity ID Check
status: DONE
project: P001
created: 2026-08-31
updated: 2026-08-31
---

## Context

Found while designing D009: a merge (`4d31306`) had already renamed a conflicting file from `A033-*.md` to `A034-*.md`, but never updated its frontmatter `id:` field — it still said `id: A033`, colliding with the real A033 (this repo's own view-rename action). `plan validate` reported zero problems: 50 entities, clean. That's because every consumer collapses parsed files into a `{entity.id: entity}` dict, and a duplicate just means the second file parsed silently overwrites the first in that dict — no error, no warning, one entity quietly vanishes from `entities`, `INDEX.md`, `generate-index`, every server.py route, everywhere.

## Fix

- Immediate: corrected the stray file's `id:` field from `A033` → `A034` to match its already-renamed filename.
- Structural: new `SchemaValidator.validate_unique_ids(files)` — takes the raw filepath-keyed parse (`PlanParser.parse_directory()`'s return value), *before* anything collapses it by ID, and errors (not warns — an ambiguous ID isn't a judgment call) if two files claim the same ID. Wired into `plan validate` as the very first check, ahead of entity/relationship validation, since a duplicate makes everything downstream unreliable.

## Verification

- Reproduced the exact bug by temporarily re-introducing the collision: `plan validate` now reports `✗ [A033] id: Claimed by 2 files: ...` and exits 1, where it previously reported "✓ Validation passed" with no indication anything was wrong.
- 3 new tests: no duplicates (silent), a real duplicate (errors, names both files), a file that failed to parse entirely is correctly excluded rather than treated as a phantom entity.

## Known gap, not fixed here

Only `plan validate`'s CLI entrypoint calls this. Every other consumer that collapses files by ID (server.py's routes, `generate-index`, `status_overview.py`) still silently does last-write-wins on a duplicate — they just won't currently know to *tell* the user via `plan validate` that a duplicate exists elsewhere. Scoped this narrowly to the primary integrity-check entrypoint rather than retrofitting every call site; worth revisiting if duplicates turn out to recur.

## Log

2026-08-31 — Implemented, tested, and verified against the real collision that motivated it. 122/122 tests pass (119 + 3 new).
