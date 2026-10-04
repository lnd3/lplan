---
id: D010
title: Outcome and InboxMessage entity types
status: DONE
project: P008
created: 2026-10-04
updated: 2026-10-04
doc_link: ""
---

## What

Two new entity types, requested and built from a real downstream need
(EphemNet, via its own agent session, 2026-10-04):

- **Outcome** (`O0xx`, `plan/outcomes/`) — a completed body of work
  written up specifically for reuse by OTHER repos/projects, not just
  this one's own history. Distinct from a Design (a spec for work not
  yet done) or an Action (a task): an Outcome exists only after real
  work shipped, and almost all its value is in its body — a
  retrospective/handoff — not its frontmatter.
- **InboxMessage** (`I0xx`, `plan/inbox/`) — a short, dated note left
  for a project's own maintainers by another project or agent (a
  tool-extension request, a cross-repo notification). Not a task to
  schedule (Action already covers that) and not a body of finished
  work (Outcome covers that) — just a record that something was
  communicated.

Out of scope: no new delivery mechanism (email, webhook, cross-repo
push) — an InboxMessage is a plain file in the receiving repo's own
`plan/inbox/`, written the same way any other entity is, by whoever
is doing the communicating (today: an agent with filesystem access to
both repos, as happened here).

## Why

EphemNet's own Stripe/paylayer integration produced real, generalizable
lessons for two sibling repos (`cinderapps`, `offgridapp`) about to do
the same integration. Writing that retrospective as a Design would
misrepresent it (a Design specifies work not yet done; this documents
work already shipped) and as an Action would bury it (Actions are
terse tasks, not retrospectives meant to be read start to end by a
different repo's maintainer). Concept's own `finding` subtype
("a validated empirical result worth preserving") was the closest
existing fit, but Concepts are meant to be short, atomic, named
abstractions — not a structured, multi-section handoff document.

**Generalization check** (per `WORKFLOW.md`'s own rule for policy
changes): both types are genuinely repo-agnostic. Any lplan-based repo
occasionally finishes work another repo will want to learn from, and
any repo occasionally wants to leave a dated note for another
project's maintainers without that note being mistaken for a task on
either side's own backlog. Neither behavior is specific to EphemNet's
own conventions.

## How

Both are plain `PlanEntity` subclasses (`src/planner/models.py`),
wired through every layer the existing six types already go through —
no new code paths invented, same shape the whole way down:

- `parser.py`: ID-prefix dispatch (`O` → Outcome, `I` → InboxMessage),
  `_parse_outcome`/`_parse_inbox_message`, and `outcomes`/`inbox`
  added to `parse_directory`'s fixed subdirs list — every CLI command
  built on top of it (`log`, `update`, `validate`, `generate-index`,
  `check-refs`) picks both up automatically with no further changes.
- `validator.py`: both join the "no additional structural constraints
  beyond frontmatter" bucket (same as Thesis/MasterPlan/Concept).
  Outcome additionally gets the same optional-parent-project warning
  Action already has, plus a same-shaped warning for unresolved
  `sources` IDs. Outcome also participates in the existing "DONE
  parent with non-terminal children" check as a project child.
- `index_gen.py`: new `## Outcomes`/`## Inbox` INDEX.md sections,
  omitted entirely (not rendered empty) when there are none — same
  convention Concepts/Theses/Master Plans already use.
- `refs.py`: `outcomes`/`inbox` added to `_ENTITY_SUBDIRS` for
  companion-link checking.
- `templates/outcome.md.template`, `templates/inbox_message.md.template`
  added, same shape as `action.md.template`.

## Where

**Architectural placement**: Same layer as every other entity type —
no new subsystem. `PlanEntity` → `parser.py` (file → model) →
`validator.py`/`index_gen.py`/`refs.py` (model → checks/reports).

**Data ownership**: Both live as plain markdown files with YAML
frontmatter in the owning repo's own `plan/outcomes/`/`plan/inbox/` —
no database, no external state. An InboxMessage's `from_project` is
free text naming the sender (not a validated cross-repo entity ref —
these are often one-off, not a standing relationship worth a real
`depends`/`enables` edge).

**Initialization & lifecycle**: Created the same way any plan file is
— hand-authored (there is no `plan new` scaffolding command for any
entity type in this CLI today), validated, committed. An InboxMessage
has no enforced lifecycle beyond its own `status` (reused loosely:
`IDEA` = unread, `DONE` = acknowledged) — nothing auto-archives or
auto-expires one.

## Constraints

- ID prefixes `O`/`I` must never collide with a future status value
  or existing prefix (checked against T/M/P/D/A/C — clear).
- `validate_id`'s own format rule (`id[0].isalpha() and id[1:].isdigit()`)
  already accepts any single leading letter — no change needed there.

## Migration

Fully additive, non-breaking: no existing entity type, field, or file
changed shape. A repo not using these two types sees no difference at
all — `outcomes`/`inbox` directories that don't exist are silently
skipped by `parse_directory`, same as `concepts`/`theses` already are
in a repo with none.

## Testability

Covered at the same layers the existing suite already tests:
`tests/test_parser.py` (round-trip parse of one file per new type),
`tests/test_validator.py` (the new project/sources warnings, and a
clean pass for InboxMessage with no refs to check),
`tests/test_index_gen.py` (both new sections appear when populated,
both absent when not). Also smoke-tested directly against the real
`bin/plan validate`/`generate-index` CLI, not just the unit suite.

## Key Decisions

- **Outcome over reusing Concept's `finding` type**: a Concept is a
  short, atomic, named abstraction; an Outcome is a structured,
  multi-section retrospective meant to be read by a different repo's
  maintainer. Different enough in shape and audience to warrant its
  own type rather than stretching Concept further.
- **InboxMessage's `from_project`/`to` as free text, not entity refs**:
  cross-repo entity references already exist (`repo:ID` syntax, see
  `refs.py`'s `_resolve_cross_repo_ref`) for STANDING dependencies
  between two repos' own plans. An inbox message is usually a one-off
  communication, not a standing relationship — forcing it through the
  same cross-repo-ref machinery would be the wrong tool for something
  this informal.
- **No new delivery mechanism**: kept deliberately dumb — a file,
  written directly into the receiving repo's own `plan/inbox/` by
  whoever (or whatever agent) is doing the communicating. Building a
  real cross-repo message-passing system was explicitly out of scope
  for what was actually asked.

## Open Questions

- Should InboxMessage eventually get its own `UNREAD`/`ACKNOWLEDGED`
  status values instead of reusing `IDEA`/`DONE`? Deferred — the reuse
  works today and adding new Status enum values is a wider-reaching
  change (the enum is shared by every entity type) than this one
  feature justifies on its own.
- Should `plan log`'s existing generic file-finder eventually grow a
  convenience command specifically for "send an inbox message to
  another repo" (writing the file directly into that OTHER repo's own
  `plan/inbox/`, not just this repo's own entities)? Not built — today
  this requires direct filesystem access to both repos, which happened
  to be available this time but won't always be.

## Related

- Project: P008 (Cross-Repo Planning Integration)
- Requested by: EphemNet, via its own agent session, alongside
  `I001` (this repo's own first real inbox message, using the feature
  this design just built to announce itself)

## Log

2026-10-04 — Design created and built in the same session, per direct
request from EphemNet's own maintainer ("Extend lplan accordingly and
then tell lplan with an inbox message"). Filed as a dedicated Design
under P008, not a silent P009 drive-by `DONE` — `WORKFLOW.md`'s own
rule is explicit that a new entity type is a policy change, never a
silent drive-by, regardless of how small the diff looks. Full
`PYTHONPATH=src python3 -m pytest tests/` green (130 passed, the same
2 pre-existing, unrelated failures in `test_status_overview.py` as
before this change). Flagged directly to the user: this changes a
file every lplan-based repo inherits, not just EphemNet's own copy.
