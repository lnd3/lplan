---
id: C004
title: Dependency Graph Analysis
type: pattern
status: STABLE
created: 2026-08-20
updated: 2026-08-26
related:
  - P002
  - D002
  - T001
---

## Goal

Use directed graph algorithms to extract insights about project structure, identify bottlenecks, compute execution phases, and detect circular dependencies.

## Pattern Description

### Graph Construction

- **Nodes** = Projects (P-prefix entities)
- **Edges** = Dependency relationships (A depends on B means A→B edge)
- **Directed** — dependency direction matters (A→B means A blocked by B)
- **Acyclic** — validated by checker; cycles reported as errors

### Algorithms

#### Topological Sort
- Compute execution order: projects with no deps can start immediately
- Transitive closure: find all upstream/downstream projects
- Breadth-first search for shortest dependency chains

#### Impact Analysis
- **Fan-in** — how many projects depend on this one
- **Fan-out** — how many projects this depends on
- **Criticality** — high fan-in + on critical path = high impact
- **Blocking power** — how many other projects this unblocks

#### Bottleneck Detection
- **Deep chains** — 5+ levels of dependencies (serializes work)
- **High fan-out** — single project blocking many others
- **Circular dependencies** — logical errors in plan
- **Critical path** — longest chain determines timeline

#### Timeline Phases
- Compute level: project with no deps = level 0
- Recursive: project's level = 1 + max(dependencies' levels)
- Phase N = all projects at level N (can run in parallel)
- Timeline = sequential execution of phases

### Implementation

- **NetworkX** library for graph algorithms
- **DependencyGraph** class wraps projects dict
- **Methods**: get_blocking_deps, get_blocked_by, find_cycles, get_topological_order
- **Performance** — O(V+E) algorithms, scales to 1000s of projects

## Benefits

- **Visibility** — see project structure at a glance
- **Planning** — compute realistic timelines from dependencies
- **Risk** — identify bottlenecks before starting work
- **Validation** — detect impossible dependency structures early
- **Analytics** — report on team velocity and parallelization

## Constraints

- **Acyclic only** — cycles indicate logical errors, must be fixed
- **Local scope** — depends field only references local projects
- **Cross-repo refs** — repo:ID syntax for external dependencies

## Log

2026-08-26 — Formalized as core lplan capability.
2026-08-20 — Pattern implemented during P002 (Tier 2 Analysis).
