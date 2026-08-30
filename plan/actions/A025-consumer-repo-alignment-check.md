---
id: A025
title: Consumer Repo Structural Alignment Check
status: DONE
priority: MEDIUM
project: P008
created: 2026-08-30
updated: 2026-08-30
---

## What was done

Added a "Consumer repo structural alignment check" subsection to
`WORKFLOW_DETAILS.md § Framework Updates`. Also updated `WORKFLOW.md §
Framework Updates` to reference it.

The check defines: when to run (after any template update), what to check
(FOCUS.md structure, REFLECTION.md one-liner format, CHANGELOG.md format,
WORKFLOW.md repo-specific-only, AXIOMS.md template preservation), and how
to diff against the template with a one-line bash command.

## Why

When lplan updates its templates, consuming repos have no prompt to re-align
their existing root plan files. Silent format drift is exactly what happened
in TradeFlow — REFLECTION.md accumulated section-header entries instead of
pipe one-liners, WORKFLOW.md restated universal rules that diverged from the
template rewrite. Neither was caught until a manual audit was requested.

The check closes this gap: it makes template alignment part of the Framework
Updates procedure, not an afterthought.

## Log

2026-08-30 — Created and completed. Drive-by from TradeFlow session, but
             explicitly flagged to user before landing (policy change to
             WORKFLOW_DETAILS.md/WORKFLOW.md — not filed under P009).
