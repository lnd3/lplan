"""Reference validation across repos and orphan detection."""

from pathlib import Path
from typing import Dict, List, Set, Tuple
from .models import PlanEntity, Project, Design, Action


def check_references(
    entities: Dict[str, PlanEntity],
    plan_dir: Path,
) -> Dict[str, any]:
    """Check entity references and flag orphans.

    Validates:
    - Local project references in depends/enables
    - Cross-repo references (repo:ID syntax)
    - Orphaned designs (parent project missing)
    - Orphaned actions (parent design missing)
    - Unused projects (no dependents, not a root)

    Args:
        entities: Dict of all entities
        plan_dir: Path to plan directory

    Returns:
        Dict with keys:
        - local_refs_checked: Count of local references validated
        - unresolvable_refs: List of {ref, hint} dicts
        - orphaned_designs: List of design IDs with missing parent project
        - orphaned_actions: List of action IDs with missing parent design
        - unused_projects: List of project IDs with no dependents/roots
        - errors: List of error messages
        - warnings: List of warning messages
    """
    report: Dict[str, any] = {
        "local_refs_checked": 0,
        "unresolvable_refs": [],
        "orphaned_designs": [],
        "orphaned_actions": [],
        "unused_projects": [],
        "errors": [],
        "warnings": [],
    }

    # Separate entities by type
    projects: Dict[str, Project] = {}
    designs: Dict[str, Design] = {}
    actions: Dict[str, Action] = {}

    for eid, entity in entities.items():
        if isinstance(entity, Project):
            projects[entity.id] = entity
        elif isinstance(entity, Design):
            designs[entity.id] = entity
        elif isinstance(entity, Action):
            actions[entity.id] = entity

    # Track which projects have dependents
    projects_with_dependents: Set[str] = set()
    root_projects: Set[str] = set(projects.keys())

    # Check project dependencies
    for project_id, project in projects.items():
        # Check depends
        for dep in project.depends:
            if dep in projects:
                report["local_refs_checked"] += 1
                projects_with_dependents.add(dep)
                root_projects.discard(project_id)
            elif ":" in dep:
                # Cross-repo reference
                report["local_refs_checked"] += 1
                # Try to resolve
                if not _resolve_cross_repo_ref(dep, plan_dir.parent):
                    report["unresolvable_refs"].append({
                        "ref": dep,
                        "from": project_id,
                        "hint": f"External ref not found: {dep}",
                    })
            else:
                report["unresolvable_refs"].append({
                    "ref": dep,
                    "from": project_id,
                    "hint": f"Project {dep} not found locally",
                })

        # Check enables
        for enabled_id in project.enables:
            if enabled_id in projects:
                report["local_refs_checked"] += 1
                projects_with_dependents.add(project_id)
            else:
                # Informational: enabled project doesn't exist (yet)
                report["warnings"].append(
                    f"Project {project_id} enables {enabled_id}, which doesn't exist"
                )

    # Check designs
    for design_id, design in designs.items():
        if design.project not in projects:
            report["orphaned_designs"].append(design_id)
            report["errors"].append(
                f"Design {design_id}: parent project {design.project} not found"
            )

    # Check actions
    for action_id, action in actions.items():
        if action.design and action.design not in designs:
            report["orphaned_actions"].append(action_id)
            report["warnings"].append(
                f"Action {action_id}: parent design {action.design} not found"
            )

    # Find unused projects (no dependents, not roots of anything)
    for project_id in projects:
        if project_id not in projects_with_dependents:
            # Not blocking any other project; check if it's a root
            project = projects[project_id]
            if not project.depends and not project.enables:
                # Truly isolated
                report["unused_projects"].append(project_id)

    return report


def _resolve_cross_repo_ref(ref: str, parent_dir: Path) -> bool:
    """Try to resolve a cross-repo reference (repo:ID format).

    Args:
        ref: Reference string like "upstream-lib:UP001"
        parent_dir: Parent directory containing submodules

    Returns:
        True if the reference can be resolved, False otherwise
    """
    try:
        repo_name, entity_id = ref.split(":", 1)
    except ValueError:
        return False

    # Look for ../repo_name/plan/projects/ID*.md
    search_dir = parent_dir / repo_name / "plan"

    if not search_dir.exists():
        return False

    # Check if the entity exists in that repo's projects
    entity_prefix = entity_id[0] if entity_id else ""
    if entity_prefix in ("P", "D", "A"):
        subdir = search_dir / f"{entity_prefix.lower()}s"
        matches = list(subdir.glob(f"{entity_id}-*.md"))
        return len(matches) > 0

    return False
