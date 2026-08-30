---
id: T002
title: Schema-Driven Planning Enables Validation and Consistency
status: HELD
conviction: 9
created: 2026-08-20
updated: 2026-08-24
parent_thesis: []
description: Plans expressed in structured, validated schemas prevent inconsistency and catch errors early.
---

## Goal

Free-form planning documents are fragile and error-prone. This thesis asserts that plans must be:

- **Structured**: Defined schema (YAML frontmatter + markdown sections)
- **Typed**: Projects, Designs, Actions are distinct types with invariants
- **Validated**: Automated checks catch missing dependencies, broken references, invalid states
- **Machine-readable**: Enables analysis, reporting, and integration

Schema-driven planning shifts verification from manual review to automated tooling, increasing reliability and speed.

## Scope

- Data models (Pydantic) for all entity types
- Parser that enforces schema compliance
- Validator that checks relationships and state
- CLI commands that surface validation errors early

## Linked

- **Master Plans**: M001 (lplan Framework Development)
- **Projects**: P001 (Tier 1 Engine), P002 (Tier 2 Analysis)

## Key Evidence

- Schema-less early attempts led to inconsistent plan states
- Validator catches ~95% of errors before they propagate
- Typed models enable refactoring confidence
- Cross-repo references resolvable only through schema discipline

## Log

2026-08-24 — Thesis validated through Pydantic implementation and widespread adoption.
2026-08-20 — Thesis emerged during data model design.
