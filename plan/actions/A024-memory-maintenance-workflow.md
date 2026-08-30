---
id: A024
title: AI Agent Memory Maintenance — Workflow Documentation
status: DONE
priority: LOW
project: P009
created: 2026-08-30
updated: 2026-08-30
---

## What was done

Added AI agent memory maintenance as a documented practice in the lplan workflow:

- `WORKFLOW.md`: new `## AI Agent Memory Maintenance` section — session-start reads, Plans section update trigger, line limit + pruning policy, automation target.
- `templates/WORKFLOW.md.template`: matching section with repo-specific customization slots.
- TradeFlow `plan/WORKFLOW.md`: created (was missing). Concrete repo-specific rules: session-start ritual, memory file path, Plans section update trigger, line limit (150), journal habit, validation step, commit convention.

## Why

MEMORY.md was at 212 lines and being silently truncated, meaning the Plans section (the only plan content guaranteed in AI context) was stale or absent. Formalising the maintenance ritual prevents drift. A009 Phase 3 will automate the Plans section generation; until then this documents the manual procedure.

## Log

2026-08-30 — Created and completed. Drive-by from TradeFlow session.
