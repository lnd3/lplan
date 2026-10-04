# Inbox Message File Schema

An inbox message is a short, dated note left for a project's own
maintainers by another project or agent — a tool-extension request, a
cross-repo notification, a "this is ready, go read it" pointer. Not a
task to schedule (see Action) and not a body of finished work to reuse
(see Outcome) — just a record that something was communicated.

## Location & Naming
- Location: `plan/inbox/`
- Naming: `I<NNN>-kebab-case-title.md`
- Examples: `I001-ephemnet-stripe-paylayer-outcome-ready.md`

## Required Frontmatter Fields
- `id`: I001, I002, etc.
- `title`: Short subject line
- `status`: reuses the shared Status enum loosely — `IDEA` means "new, not yet acted on," `DONE` means "read/acknowledged." Any other value is unusual for this type.
- `created`: YYYY-MM-DD
- `updated`: YYYY-MM-DD

## Optional Frontmatter Fields
- `from_project`: Free text naming the sender, e.g. `EphemNet` — not a validated cross-repo entity reference (see Notes)
- `to`: Free text naming the recipient, e.g. `lplan maintainers` or `cinderapps maintainers`
- `description`: One-line summary

## Content Sections

### ## Message
What happened, what changed, or what's being requested — short and
concrete. Link to the real source (a commit, a file, another repo's
own plan entity) rather than re-explaining it at length here.

### ## Log
Append-only record — typically just when it was sent, and later, when
it was read/acknowledged.

Format: `YYYY-MM-DD — Note.`

## Notes

- `from_project`/`to` are free text, not `repo:ID` cross-repo
  references (see `refs.py`'s `_resolve_cross_repo_ref` for that
  separate mechanism). A standing dependency between two repos' own
  plans deserves a real reference; a one-off communication doesn't
  need that machinery.
- No delivery mechanism is implied — a message is a plain file,
  written directly into the RECEIVING repo's own `plan/inbox/` by
  whoever (or whatever agent) is doing the communicating. If the
  sender and receiver are different repos on the same machine, that
  just means direct filesystem access; nothing here assumes more than
  that.
- Keep it short. If the content is substantial enough to need its own
  structure (a retrospective, a handoff), write that as an Outcome in
  the SENDING repo and send a message that just points to it — don't
  duplicate a long document into the message itself.

## Example

```yaml
---
id: I001
title: EphemNet's Stripe/paylayer integration handoff (O001) is ready
status: IDEA
from_project: EphemNet
to: cinderapps maintainers
created: 2026-10-04
updated: 2026-10-04
---

## Message

EphemNet finished its Stripe billing rail. Written up for cinderapps/
offgridapp specifically: [O001](../../../EphemNet/plan/outcomes/O001-stripe-paylayer-integration-handoff.md).

## Log

2026-10-04 — Sent.
```
