"""Git operations with plan governance."""

import subprocess
import sys
from pathlib import Path
from .parser import PlanParser
from .validator import SchemaValidator
from .graph import DependencyGraph


def governed_commit(plan_dir: Path, message: str) -> None:
    """Commit plan changes after full validation.

    Runs schema validation, relationship validation, and cycle detection.
    On success, stages plan_dir and commits with message.
    On failure, aborts and reports all errors.

    Args:
        plan_dir: Path to plan directory
        message: Commit message

    Raises:
        RuntimeError: If validation fails or git command fails
    """
    plan_dir = Path(plan_dir)

    # 1. Parse all entities
    parsed = PlanParser.parse_directory(plan_dir)

    # Separate successful parses from errors
    entities = {}
    parse_errors = []

    for file_path, result in parsed.items():
        if isinstance(result, dict) and "error" in result:
            parse_errors.append(f"{file_path}: {result['error']}")
        else:
            entity = result.entity
            entities[entity.id] = entity

    if parse_errors:
        raise RuntimeError(
            "✗ Parse errors:\n  " + "\n  ".join(parse_errors)
        )

    # 2. Validate schema
    validator = SchemaValidator()
    validator.validate_entity(*entities.values())

    if validator.errors:
        error_msgs = [f"{e.entity_id}: {e.message}" for e in validator.errors]
        raise RuntimeError(
            "✗ Schema validation failed:\n  " + "\n  ".join(error_msgs)
        )

    if validator.warnings:
        warning_msgs = [f"{e.entity_id}: {e.message}" for e in validator.warnings]
        print("⚠ Warnings:", file=sys.stderr)
        for warn in warning_msgs:
            print(f"  {warn}", file=sys.stderr)

    # 3. Validate relationships
    validator.validate_relationships(entities)

    if validator.errors:
        error_msgs = [f"{e.entity_id}: {e.message}" for e in validator.errors]
        raise RuntimeError(
            "✗ Relationship validation failed:\n  " + "\n  ".join(error_msgs)
        )

    # 4. Check for cycles (Project entities only)
    projects = {eid: e for eid, e in entities.items() if hasattr(e, "priority")}

    if projects:
        graph = DependencyGraph(projects)
        if graph.has_cycles():
            cycles = graph.find_cycles()
            cycle_strs = [" → ".join(c) for c in cycles]
            raise RuntimeError(
                "✗ Dependency cycles detected:\n  " + "\n  ".join(cycle_strs)
            )

    # 5. All validations passed; commit
    try:
        # Stage the plan directory
        subprocess.run(
            ["git", "add", str(plan_dir)],
            check=True,
            capture_output=True,
            text=True,
        )

        # Commit
        full_message = f"plan: {message}"
        subprocess.run(
            ["git", "commit", "-m", full_message],
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"✓ Committed: {full_message}")

    except FileNotFoundError:
        raise RuntimeError("✗ Git not found. Ensure git is installed and in PATH.")
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr:
            print("ℹ No changes to commit")
        else:
            raise RuntimeError(
                f"✗ Git commit failed: {e.stderr or e.stdout}"
            )
