#!/bin/bash
# init-repo.sh — Initialize plan/ directory in a repository

set -euo pipefail

REPO_NAME="${1:?Repository name required (e.g., 'TradeFlow')}"
REPO_ROLE="${2:-Core repository}"
TARGET_DIR="${3:-.}"

if [[ ! -d "$TARGET_DIR" ]]; then
    mkdir -p "$TARGET_DIR"
fi

PLAN_DIR="$TARGET_DIR/plan"

if [[ -d "$PLAN_DIR" ]]; then
    echo "Plan directory already exists at $PLAN_DIR"
    exit 1
fi

echo "Initializing plan directory for: $REPO_NAME"
echo "Role: $REPO_ROLE"
echo

# Create structure
mkdir -p "$PLAN_DIR"/{projects,designs,actions}
echo "✓ Created directory structure"

# Create README
cat > "$PLAN_DIR/README.md" << 'EOF'
# Planning System

This directory contains the planning structure for this repository, managed via planner-framework.

See `.planner-framework/README.md` for system documentation.

## Quick Start

- **INDEX.md**: Master overview and status
- **projects/**: High-level goals and scope
- **designs/**: Architectural specifications
- **actions/**: Concrete task lists
- **CHANGELOG.md**: Append-only status change log

## Tools

- `.planner-framework/tools/validate.sh plan/` — Validate structure
- `.planner-framework/tools/aggregate-local.sh` — Aggregate submodule plans (if any)
EOF
echo "✓ Created README.md"

# Create INDEX.md
cat > "$PLAN_DIR/INDEX.md" << EOF
# $REPO_NAME Plan Index

*Last updated: $(date +%Y-%m-%d)*

Status: \`IDEA\` · \`PLANNING\` · \`IN_PROGRESS\` · \`BLOCKED\` · \`DONE\` · \`DEFERRED\` · \`CANCELLED\`

---

## Projects

| ID | Title | Status | Priority | Key Open Work |
| --- | --- | --- | --- | --- |
| [P001](projects/P001-example.md) | Example Project | IDEA | LOW | Define scope |

---

## Designs

| ID | Title | Status | Project | Doc |
| --- | --- | --- | --- | --- |
| [D001](designs/D001-example.md) | Example Design | IDEA | P001 | — |

---

## Actions

| ID | Title | Status | Design | Open Tasks |
| --- | --- | --- | --- | --- |
| [A001](actions/A001-example.md) | Example Action | IDEA | D001 | TBD |
EOF
echo "✓ Created INDEX.md"

# Create CHANGELOG.md
cat > "$PLAN_DIR/CHANGELOG.md" << 'EOF'
# Plan Changelog

Append-only record of all status and priority changes.

Format: `YYYY-MM-DD | ID | old_status → new_status | note`

---
EOF
echo "✓ Created CHANGELOG.md"

# Create example project
cat > "$PLAN_DIR/projects/P001-example.md" << 'EOF'
---
id: P001
title: Example Project
status: IDEA
priority: LOW
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-20
depends: []
external_dependencies: []
enables: []
---

## Goal

Define what this project achieves.

## Scope

- Item A
- Item B

## Linked

- **Projects**: (other projects)
- **Designs**: (designs)
- **Actions**: (actions)

## Tasks

- [ ] Task 1
- [ ] Task 2

## Log

2026-08-20 — Project created (template).
EOF
echo "✓ Created example project (P001)"

echo
echo "✓ Plan directory initialized at: $PLAN_DIR"
echo
echo "Next steps:"
echo "  1. Edit plan/projects/P001-example.md with your first real project"
echo "  2. Create designs/ and actions/ files as needed"
echo "  3. Update plan/INDEX.md to reflect your work"
echo "  4. Run '.planner-framework/tools/validate.sh plan/' to check structure"
echo
echo "See .planner-framework/schema/ for complete documentation."
