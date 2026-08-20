#!/bin/bash
# aggregate-local.sh — DEPRECATED: Use Python engine instead
#
# This script is no longer developed. For multi-repo aggregation, use:
#   ./bin/plan graph-report plan/       # See cross-repo dependencies
#   ./bin/plan check-refs plan/         # Verify cross-repo references
#
# The Python engine provides full dependency analysis and querying.
# See README.md for more information.

set -euo pipefail

REPO_ROOT="${1:-.}"
COMMAND="${2:-full}"

echo "Aggregating plans from $REPO_ROOT"
echo

# Find all plan directories
echo "Discovering plan directories..."
plans=()
while IFS= read -r plan_dir; do
    repo_name=$(basename "$(dirname "$plan_dir")")
    plans+=("$plan_dir:$repo_name")
    echo "  Found: $plan_dir (repo: $repo_name)"
done < <(find "$REPO_ROOT" -type d -name "plan" -not -path "./.git/*" | sort)

if [[ ${#plans[@]} -eq 0 ]]; then
    echo "No plan directories found."
    exit 1
fi

echo
echo "Checking project files..."
total_projects=0
for plan_entry in "${plans[@]}"; do
    plan_dir="${plan_entry%:*}"
    repo_name="${plan_entry#*:}"

    project_count=$(find "$plan_dir/projects" -name "*.md" 2>/dev/null | wc -l || echo 0)
    ((total_projects+=project_count))
    echo "  $repo_name: $project_count projects"
done

echo
echo "Summary:"
echo "  Total repos: ${#plans[@]}"
echo "  Total projects: $total_projects"

case $COMMAND in
    validate)
        echo
        echo "Running validation (no modifications)..."
        for plan_entry in "${plans[@]}"; do
            plan_dir="${plan_entry%:*}"
            repo_name="${plan_entry#*:}"
            echo
            echo "Validating $repo_name..."
            # Placeholder for validation logic
            echo "  (validation logic goes here)"
        done
        ;;
    dry-run)
        echo
        echo "Dry run: Would generate aggregated views"
        echo "  (generation logic goes here)"
        ;;
    *)  # full (default)
        echo
        echo "Full aggregation: generating outputs"
        # Placeholder for full aggregation and commit logic
        echo "  (aggregation logic goes here)"
        ;;
esac

echo
echo "Aggregation complete."
