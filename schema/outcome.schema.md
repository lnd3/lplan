# Outcome File Schema

An outcome file documents a completed body of work, written up
specifically for reuse by OTHER repos/projects — not just this one's
own history. Distinct from a design (a spec for work not yet done) or
an action (a concrete task): an outcome exists only after real work
shipped, and almost all its value is in its body — a retrospective or
handoff — not its frontmatter.

## Location & Naming
- Location: `plan/outcomes/`
- Naming: `O<NNN>-kebab-case-title.md`
- Examples: `O001-stripe-paylayer-integration-handoff.md`

## Required Frontmatter Fields
- `id`: O001, O002, etc.
- `title`: Outcome title
- `status`: IDEA, PLANNING, IN_PROGRESS, BLOCKED, DONE, DEFERRED, CANCELLED (typically DONE — the work it documents has already shipped)
- `created`: YYYY-MM-DD
- `updated`: YYYY-MM-DD

## Optional Frontmatter Fields
- `project`: Parent project ID, if any (e.g., P001)
- `audience`: List of other repos/projects this was written for, e.g. `[cinderapps, offgridapp]`
- `sources`: List of design/action IDs this outcome distills (e.g. `[D010, D012]`)
- `description`: One-line summary

## Content Sections

Free-form beyond the Log — an outcome's own shape should fit what it's
documenting, not a rigid template. A real one typically covers:

### Why this exists
What was built, and why is it worth writing up for OTHER repos/
projects specifically — not just this one's own history (that's what
`sources`' own Log sections already cover).

### What we started from
The state of things before this work — existing libraries, prior art,
what was already proven vs. still open.

### What we built
The concrete shape of the finished thing — architecture, key files,
decisions that mattered.

### Gotchas for the next integration
Specific pitfalls hit along the way, named plainly enough that a
different repo doing the same integration can avoid them without
re-deriving them from scratch.

### ## Log
Append-only record.

Format: `YYYY-MM-DD — Note.`

## Notes

- Written for a DIFFERENT repo's maintainer to read start to end — not
  terse like an action, not a spec for work not yet done like a
  design.
- If the audience never reads it, it didn't do its job — write for the
  reader's actual decision-making, not as a historical record of this
  repo's own process.
- Prefer concrete pitfalls over general advice — "we hit X, caused by
  Y, fixed by Z" over "be careful about X."

## Example

```yaml
---
id: O001
title: Stripe/paylayer integration handoff — from EphemNet's own build-out, for cinderapps and offgridapp
status: DONE
project: P001
audience: [cinderapps, offgridapp]
sources: [D010, D011, D012]
created: 2026-10-04
updated: 2026-10-04
---

## Why this exists

EphemNet built a complete, real-money Stripe billing rail on top of
`paylayer` from a near-empty starting point. `cinderapps` and
`offgridapp` are both expected to do the same integration later —
this document exists so that work starts from EphemNet's own real
decisions and real mistakes, not from zero.

## What we started from
...

## What we built
...

## Gotchas for the next integration

1. Webhook idempotency is not optional...
2. Metadata-driven redemption, trust nothing else...

## Log

2026-10-04 — Written up per direct request.
```
