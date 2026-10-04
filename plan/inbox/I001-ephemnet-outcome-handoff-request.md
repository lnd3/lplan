---
id: I001
title: EphemNet requested Outcome/InboxMessage entity types for a Stripe integration handoff doc
status: DONE
from_project: EphemNet
to: lplan maintainers
created: 2026-10-04
updated: 2026-10-04
---

## Message

EphemNet needed to write up its own Stripe/paylayer integration work
as a reusable handoff document for two sibling repos about to do the
same integration (`cinderapps`, `offgridapp`). Neither Design (specifies
work not yet done) nor Action (a terse task) fit a finished
retrospective meant to be read start-to-end by a different repo's
maintainer — closest existing fit was Concept's own `finding` subtype,
but that's meant for short, atomic, named abstractions, not a
structured multi-section handoff.

Built two new entity types directly in this repo to cover it —
**Outcome** (`O0xx`, `plan/outcomes/`) for exactly that kind of
cross-repo-reusable retrospective, and **InboxMessage** (`I0xx`,
`plan/inbox/`, this very file) for a short, dated note from one
project to another's maintainers that isn't a task or a finished
body of work either. Full design, rationale, and the generalization
check: [D010](../designs/D010-outcome-and-inbox-entity-types.md).

This is the first real InboxMessage — using the feature to announce
itself, per the requesting user's own instruction ("tell lplan with
an inbox message").

## Log

2026-10-04 — Sent. Full test suite green
(`PYTHONPATH=src python3 -m pytest tests/`, 130 passed, same 2
pre-existing unrelated failures as before this change). D010 filed
under P008, not a silent P009 drive-by, per `WORKFLOW.md`'s own rule
that a new entity type is always a policy change.
