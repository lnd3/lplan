# Frontmatter Specification

All plan files (project, design, action) use YAML frontmatter to store structured metadata.

## Format

```yaml
---
field1: value1
field2: value2
---

# Content starts here
```

## Common Fields (All Files)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Unique identifier (P001, D001, A001, L001, etc.) Scope: local to repo. Prefix indicates type: P=project, D=design, A=action. |
| `title` | string | YES | Human-readable title |
| `status` | enum | YES | One of: IDEA, PLANNING, IN_PROGRESS, BLOCKED, DONE, DEFERRED, CANCELLED |
| `created` | date | YES | ISO 8601 (YYYY-MM-DD) |
| `updated` | date | YES | ISO 8601; update when status/priority changes |
| `description` | string | NO | One-line summary for INDEX display |

## Project-Specific Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `priority` | enum | YES | HIGH, MEDIUM, LOW |
| `priority_drivers` | list | NO (default `[]`) | List of driver keys (see priority-framework.md). May be omitted at parse time, but the validator requires it non-empty and every key to match a known driver — see priority-framework.md. |
| `depends` | list | NO | Projects this depends on, as "repo:ID" refs (e.g., `["tradeflow:P001", "ltools:L001"]`) |
| `external_dependencies` | list | NO | Dependencies on external repos/features not formalized as projects |
| `enables` | list | NO | Projects this unblocks when complete, as "repo:ID" refs |
| `project` | string | NO | Parent project ID if this is a sub-initiative |

### Example

```yaml
---
id: P005
title: HyperLiquid API Integration
status: PLANNING
priority: HIGH
priority_drivers:
  - critical_live_path_only
created: 2026-08-20
updated: 2026-08-20
depends: []
external_dependencies:
  - repo: ltools
    feature: "Node IDs 10600+ reserved"
    status: "DONE (D001)"
    blocking: false
enables:
  - tradeflow:P001
---

## Goal
A standalone HyperLiquid exchange integration...
```

## Design-Specific Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | YES | Parent project ID (e.g., P001) |
| `status` | enum | YES | IDEA, PLANNING, IN_PROGRESS, DONE, DEFERRED, CANCELLED (no BLOCKED for designs) |

### Example

```yaml
---
id: D001
title: Anchored Volume Levels V3
status: DONE
project: P001
created: 2026-05-30
updated: 2026-08-20
external_dependencies: []
---

## Summary
...
```

## Action-Specific Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `design` | string | NO | Parent design ID (e.g., D001) |
| `project` | string | NO | Associated project ID |
| `status` | enum | YES | IDEA, PLANNING, IN_PROGRESS, BLOCKED, DONE, DEFERRED, CANCELLED |
| `priority` | enum | NO | If action is independent, may have priority |

### Example

```yaml
---
id: A001
title: Signal Node Correctness — Post-Audit Items
status: IN_PROGRESS
design: D002
project: P001
created: 2026-05-30
updated: 2026-08-20
---

## Context
...
```

## Notes

- **Dates**: Always YYYY-MM-DD. Tools can parse these reliably.
- **Lists**: Use YAML list syntax `[item1, item2]` or multi-line `- item` format.
- **Cross-Repo Refs**: Format is always `repo:ID` (lowercase repo name, uppercase ID). Example: `tradeflow:P001`, `ltools:L002`.
- **Repo Names**: Use directory name or short identifier. Resolve via `repos.yml` or discovery.
- **External Dependencies**: When a feature isn't formalized as a project, document as object with `repo`, `feature`, `status`, `blocking`.
- **Optional Fields**: Omit if not applicable. Tools should handle missing fields gracefully.
