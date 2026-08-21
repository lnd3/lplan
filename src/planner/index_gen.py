"""Index and changelog generation for plan visibility."""

from datetime import date, datetime
from pathlib import Path
from typing import Dict, List
from .models import PlanEntity, Project, Design, Action


def generate_index(
    entities: Dict[str, PlanEntity],
    repo_name: str,
) -> str:
    """Generate INDEX.md markdown.

    Args:
        entities: Dict mapping entity paths or IDs to PlanEntity objects
        repo_name: Name of the repository (used in heading)

    Returns:
        Markdown string ready to write to INDEX.md
    """
    # Separate entities by type
    projects: Dict[str, Project] = {}
    designs: Dict[str, Design] = {}
    actions: Dict[str, Action] = {}

    for entity_id, entity in entities.items():
        if isinstance(entity, Project):
            projects[entity.id] = entity
        elif isinstance(entity, Design):
            designs[entity.id] = entity
        elif isinstance(entity, Action):
            actions[entity.id] = entity

    # Build markdown
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        f"# {repo_name} Plan Index",
        "",
        f"*Last updated: {timestamp}*",
        "",
        "Status: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`",
        "",
        "---",
        "",
        "## Projects",
        "",
        "| ID | Title | Status | Priority | Key Open Work |",
        "| --- | --- | --- | --- | --- |",
    ]

    for pid, project in sorted(projects.items()):
        # Find first unchecked task if any
        first_task = "TBD"
        if project.id.startswith("P"):
            # Try to find a file path for link
            link = f"projects/{pid}-{project.title.lower().replace(' ', '-')}.md"
        else:
            link = f"projects/{pid}.md"

        lines.append(f"| [{pid}]({link}) | {project.title} | {project.status.value} | {project.priority.value} | {first_task} |")

    lines.extend([
        "",
        "---",
        "",
        "## Designs",
        "",
        "| ID | Title | Status | Project | Doc |",
        "| --- | --- | --- | --- | --- |",
    ])

    for did, design in sorted(designs.items()):
        link = f"designs/{did}-{design.title.lower().replace(' ', '-')}.md"
        project_ref = design.project if design.project else "—"
        lines.append(f"| [{did}]({link}) | {design.title} | {design.status.value} | {project_ref} | (link if applicable) |")

    lines.extend([
        "",
        "---",
        "",
        "## Actions",
        "",
        "| ID | Title | Status | Design | Open Tasks |",
        "| --- | --- | --- | --- | --- |",
    ])

    for aid, action in sorted(actions.items()):
        link = f"actions/{aid}-{action.title.lower().replace(' ', '-')}.md"
        design_ref = action.design if action.design else "—"
        lines.append(f"| [{aid}]({link}) | {action.title} | {action.status.value} | {design_ref} | TBD |")

    return "\n".join(lines)


def write_index(plan_dir: Path, entities: Dict[str, PlanEntity], repo_name: str = "Plan") -> Path:
    """Write INDEX.md to plan directory.

    Args:
        plan_dir: Path to plan directory
        entities: Dict of entities to include
        repo_name: Name for the index heading

    Returns:
        Path to written INDEX.md
    """
    index_path = plan_dir / "INDEX.md"
    content = generate_index(entities, repo_name)
    index_path.write_text(content, encoding="utf-8")
    return index_path


def append_changelog(
    plan_dir: Path,
    entity_id: str,
    old_status: str,
    new_status: str,
    note: str,
    change_date: date = None,
) -> None:
    """Append entry to CHANGELOG.md.

    Creates file from template if it doesn't exist.

    Args:
        plan_dir: Path to plan directory
        entity_id: Entity ID being changed
        old_status: Previous status
        new_status: New status
        note: Description of the change
        change_date: Date of the change (default: today)
    """
    if change_date is None:
        change_date = date.today()

    changelog_path = plan_dir / "CHANGELOG.md"

    # Create from template if missing
    if not changelog_path.exists():
        template_content = """# Plan Changelog

Append-only record of all status and priority changes.

Format: `YYYY-MM-DD | ID | old_status → new_status | note`

---

"""
        changelog_path.write_text(template_content, encoding="utf-8")

    # Read existing content
    content = changelog_path.read_text(encoding="utf-8")

    # Append new entry (after the --- separator)
    lines = content.rstrip().split("\n")

    # Find where to insert (after the --- line)
    separator_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            separator_idx = i
            break

    # New entry
    new_entry = f"{change_date.isoformat()} | {entity_id} | {old_status} → {new_status} | {note}"

    # Insert after the separator (or at end if no separator found)
    if separator_idx >= 0:
        lines.insert(separator_idx + 1, "")
        lines.insert(separator_idx + 2, new_entry)
    else:
        lines.append("")
        lines.append(new_entry)

    changelog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
