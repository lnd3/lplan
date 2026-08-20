#!/bin/bash
# validate.sh — Validate a plan/ directory against planner-framework schema

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
PLAN_DIR="${1:-.}"

if [[ ! -d "$PLAN_DIR" ]]; then
    echo "Error: Plan directory '$PLAN_DIR' not found"
    exit 1
fi

ERRORS=0
WARNINGS=0

log_error() {
    echo "  ✗ $1" >&2
    ((ERRORS++))
}

log_warn() {
    echo "  ⚠ $1" >&2
    ((WARNINGS++))
}

log_ok() {
    echo "  ✓ $1"
}

echo "Validating plan directory: $PLAN_DIR"
echo

# Check directory structure
echo "Checking directory structure..."
for dir in projects designs actions; do
    if [[ ! -d "$PLAN_DIR/$dir" ]]; then
        log_warn "Missing $dir/ directory"
    else
        log_ok "$dir/ exists"
    fi
done
echo

# Check INDEX.md
echo "Checking INDEX.md..."
if [[ ! -f "$PLAN_DIR/INDEX.md" ]]; then
    log_error "Missing INDEX.md"
else
    if grep -q "^# " "$PLAN_DIR/INDEX.md"; then
        log_ok "INDEX.md has title"
    else
        log_warn "INDEX.md missing title"
    fi
    if grep -q "Last updated" "$PLAN_DIR/INDEX.md"; then
        log_ok "INDEX.md has timestamp"
    else
        log_warn "INDEX.md missing 'Last updated' field"
    fi
fi
echo

# Check project files
echo "Checking project files..."
project_count=0
for project_file in "$PLAN_DIR"/projects/*.md 2>/dev/null || true; do
    if [[ ! -f "$project_file" ]]; then
        continue
    fi
    ((project_count++))
    filename=$(basename "$project_file")

    # Extract ID from filename (P001-... → P001)
    id=$(echo "$filename" | sed 's/^\([^-]*\).*/\1/')

    # Check for required frontmatter
    if grep -q "^id: " "$project_file"; then
        log_ok "$filename: has id field"
    else
        log_error "$filename: missing id field"
    fi

    if grep -q "^title: " "$project_file"; then
        log_ok "$filename: has title"
    else
        log_error "$filename: missing title"
    fi

    if grep -q "^status: " "$project_file"; then
        log_ok "$filename: has status"
    else
        log_error "$filename: missing status"
    fi

    if grep -q "^priority: " "$project_file"; then
        log_ok "$filename: has priority"
    else
        log_error "$filename: missing priority"
    fi

    if grep -q "^priority_drivers: " "$project_file"; then
        log_ok "$filename: has priority_drivers"
    else
        log_error "$filename: missing priority_drivers"
    fi
done
echo "  Found $project_count project files"
echo

# Check CHANGELOG
echo "Checking CHANGELOG.md..."
if [[ -f "$PLAN_DIR/CHANGELOG.md" ]]; then
    log_ok "CHANGELOG.md exists"
    if grep -q "^[0-9]" "$PLAN_DIR/CHANGELOG.md"; then
        log_ok "CHANGELOG.md has entries"
    else
        log_warn "CHANGELOG.md appears empty"
    fi
else
    log_warn "CHANGELOG.md not found"
fi
echo

# Summary
echo "===================================="
if [[ $ERRORS -eq 0 ]]; then
    echo "✓ Validation passed"
    if [[ $WARNINGS -gt 0 ]]; then
        echo "  ($WARNINGS warnings)"
    fi
    exit 0
else
    echo "✗ Validation failed"
    echo "  $ERRORS errors, $WARNINGS warnings"
    exit 1
fi
