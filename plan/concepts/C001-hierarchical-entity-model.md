---
id: C001
title: Hierarchical Entity Model
type: pattern
status: STABLE
created: 2026-08-20
updated: 2026-08-26
related:
  - T001
  - M001
  - P005
  - P006
---

## Goal

A five-level hierarchy for organizing planning concerns from strategic vision to concrete execution:

**Thesis** → **Master Plan** → **Project** → **Design** → **Action**

Each level serves a distinct purpose and audience, with clear separation of concerns.

## Scope

### Layer Definitions

1. **Thesis** (T-prefix) — Foundational beliefs about how the world works
   - Conviction: 1-10 scale of confidence
   - Status: HELD, QUESTIONING, ABANDONED
   - Example: "Async improves UX" (T003)

2. **Master Plan** (M-prefix) — Long-term strategic visions and goals
   - Stakeholder-owned across 5-year outlook
   - Informs which projects get built
   - Example: "Developer Experience Excellence" (M001)

3. **Project** (P-prefix) — High-level goals and initiatives
   - Can depend on other projects or external systems
   - Decomposed into designs
   - Example: "Web Server UI Refactoring" (P004)

4. **Design** (D-prefix) — Architectural specifications
   - Belongs to exactly one project
   - Decomposed into actions
   - Example: "JavaScript Module Architecture" (D003)

5. **Action** (A-prefix) — Concrete implementation tasks
   - Belongs to a design (and implicitly its parent project)
   - Smallest unit of work tracking
   - Example: "Extract UI module" (A004)

## Key Constraints

- **Belongs-to**: Design belongs to Project, Action belongs to Design
- **Depends-on**: Can exist between same-level or across levels (Project→Project, Action→Action)
- **Enables**: One-way relationship indicating unblocking
- **Parent references**: Lower levels reference their parent (not upward)
- **No cycles**: Dependency graph must be acyclic

## Benefits

- **Cognitive fit**: Each level targets decision-makers at that scope
- **Scalability**: Thousands of actions roll up cleanly to dozens of projects
- **Traceability**: Follow ideas from thesis → master plan → project → design → action
- **Parallelization**: Designs under one project can be worked in parallel
- **Cross-repo**: Master plans (upstream) seed projects (downstream)

## Log

2026-08-26 — Formalized as foundational pattern.
2026-08-20 — Pattern emerged during lplan architecture design.
