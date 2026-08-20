---
id: D001
title: Priority Scoring Engine Design
status: DONE
project: P001
created: 2026-08-20
updated: 2026-08-20
description: Core algorithm for computing project priority from drivers
---

## Goal

Design and implement programmatic priority scoring from driver definitions. Compute priority scores based on weighted drivers, with support for framework and custom drivers.

## Scope

- Core driver definitions (8 drivers with weights)
- Custom driver support per-repo
- Score computation algorithm
- Score-to-priority mapping
- Mismatch detection (computed vs declared)
- Analysis output with driver breakdown

## Implementation

Implemented in `src/planner/priority.py`:
- `PriorityEngine` class
- `compute_score()` method
- `score_to_priority()` mapping
- `analyze_project()` detailed breakdown
- Support for custom drivers

## Log

2026-08-20 — Implementation complete. All priority tests passing.
