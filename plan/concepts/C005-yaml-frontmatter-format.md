---
id: C005
title: YAML Frontmatter Format
type: rule
status: STABLE
created: 2026-08-20
updated: 2026-08-26
related:
  - T002
  - P001
  - C001
---

## Goal

A standardized YAML frontmatter block (---\nYAML\n---) separating machine-readable metadata from human-readable content, enabling validation, parsing, and cross-referencing.

## Format Rules

### Required Fields (All Entities)
```yaml
---
id:       <TYPE><NUMBER>     # P001, D001, T001, M001, C001, etc.
title:    <string>           # Concise name (no metadata, no file refs)
status:   <enum>             # Entity-type-specific status
created:  YYYY-MM-DD         # ISO date when entity created
updated:  YYYY-MM-DD         # ISO date of last modification
---
```

### Optional Fields (Variable by Type)

**Project (P-prefix)**
- priority: HIGH | MEDIUM | LOW
- priority_drivers: [list of drivers]
- depends: [list of P-IDs or repo:ID]
- enables: [list of P-IDs]
- parent_master_plan: [list of M-IDs]

**Design (D-prefix)**
- project: P-ID (required)

**Action (A-prefix)**
- design: D-ID
- project: P-ID
- priority: HIGH | MEDIUM | LOW

**Thesis (T-prefix)**
- conviction: 1-10 (integer)
- parent_thesis: [list of T-IDs]

**Master Plan (M-prefix)**
- stakeholder: string
- vision: string
- goals: [list of strings]
- priority: HIGH | MEDIUM | LOW

**Concept (C-prefix)**
- type: mode | term | pattern | constraint | rule | finding
- related: [list of IDs, file references]

### Markdown Body

After closing `---`, document structure:
```markdown
## Goal
Description of what this achieves and why

## Scope
What's included/excluded

## Linked
Related entities and references

## Tasks
For projects/theses: work breakdown

## Log
Append-only activity log (most recent first)
```

## Validation Rules

- **ID format** — must match entity type prefix + digits (P001, not P-001)
- **Title length** — typically 2-5 words, < 80 characters
- **Status enums** — must match entity-type-specific status values
- **Date format** — ISO 8601 (YYYY-MM-DD) only
- **References** — IDs must exist in local plan or use repo:ID syntax
- **No cycles** — dependency graph must be acyclic
- **Type constraints** — Design must have project parent, Action must have parent

## Benefits

- **Parseable** — frontmatter extractable by YAML parser
- **Versionable** — plain text, diff-friendly
- **Structured** — enables validation and analytics
- **Decoupled** — metadata separate from content
- **Linkable** — IDs enable cross-references

## Implementation

- **Parser** — splits on `---` delimiter, parses YAML, extracts sections
- **Validator** — checks required fields, type constraints, reference validity
- **CLI** — all commands parse via PlanParser.parse_file()
- **Web UI** — frontmatter rendered as badges, metadata panels

## Log

2026-08-26 — Formalized as core lplan constraint.
2026-08-20 — Format established during T001 (Tier 1 Engine) design.
