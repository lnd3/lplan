---
id: T001
title: Planning Tools Must Separate Strategic Vision from Tactical Execution
status: HELD
conviction: 9
created: 2026-08-20
updated: 2026-08-24
parent_thesis: []
description: Effective planning requires separating long-term strategic thinking (what direction) from short-term tactical work (how to get there).
---

## Goal

Planning failures often stem from conflating strategic decisions with execution details. This thesis asserts that a planning framework must provide clear separation between:

- **Strategic layer** (theses, master plans): Long-term visions, foundational beliefs, organizational direction
- **Execution layer** (projects, designs, actions): Concrete tasks, dependencies, timelines

This separation enables stakeholders at different levels to operate at appropriate abstraction levels without friction.

## Scope

- Planning tool architecture and data models
- Hierarchical entity types (thesis → master_plan → project → design → action)
- Validation rules that enforce layer boundaries
- UI/UX that visualizes the layers clearly

## Linked

- **Master Plans**: M001 (lplan Framework Development)
- **Projects**: P001 (Tier 1 Engine), P004 (Web Refactoring), P005 (Master Plans)

## Key Evidence

- Early monolithic approaches mixed strategy and tactics, causing scope creep
- Separating concerns enabled faster iteration and clearer accountability
- Multi-level organization can navigate plan without cognitive overload

## Log

2026-08-24 — Thesis formalized as foundational belief driving lplan architecture.
2026-08-20 — Initial hypothesis during engine design phase.
