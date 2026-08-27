"""Index and changelog generation for plan visibility."""

from datetime import date, datetime
from pathlib import Path
from typing import Dict, List
from .models import PlanEntity, Project, Design, Action, Thesis, MasterPlan, Concept


def detect_repo_name(plan_dir: Path) -> str:
    """Best-effort repo name for a plan directory.

    Precedence: explicit .plan-config override, then README.md's first `#`
    heading (the stable, human-maintained ground truth for a repo's name —
    the same fact INDEX.md's heading and the web UI's title/tab need), then
    a guess from the containing directory's name as a last resort. plan_dir's
    own name is always literally "plan", so it's the *containing* repo
    directory that actually identifies which plan this is.
    """
    plan_path = Path(plan_dir)
    repo_name = ""

    config_path = plan_path / ".plan-config"
    if config_path.exists():
        try:
            for line in config_path.read_text().splitlines():
                if line.startswith("repo_name="):
                    repo_name = line.split("=", 1)[1].strip()
                    break
        except Exception:
            pass

    abs_plan_path = plan_path.resolve()
    parent_name = abs_plan_path.parent.name
    repo_root = abs_plan_path.parent.parent if parent_name.lower() == "plan" else abs_plan_path.parent

    if not repo_name:
        readme = repo_root / "README.md"
        if readme.exists():
            try:
                for line in readme.read_text(encoding="utf-8").splitlines():
                    stripped = line.strip()
                    if stripped.startswith("# "):
                        repo_name = stripped[2:].strip()
                        break
            except Exception:
                pass

    if not repo_name:
        repo_name = repo_root.name
        if "-" in repo_name or "_" in repo_name:
            repo_name = repo_name.replace("-", " ").replace("_", " ").title()

    return repo_name or "Plan"


def generate_index(
    entities: Dict[str, PlanEntity],
    repo_name: str,
    id_to_filename: Dict[str, str] = None,
) -> str:
    """Generate INDEX.md markdown.

    Args:
        entities: Dict mapping entity IDs to PlanEntity objects
        repo_name: Name of the repository (used in heading)
        id_to_filename: Dict mapping entity ID to actual filename (e.g., "P001" → "P001-price-levels-strategy.md")

    Returns:
        Markdown string ready to write to INDEX.md
    """
    if id_to_filename is None:
        id_to_filename = {}

    # Separate entities by type
    concepts: Dict[str, Concept] = {}
    theses: Dict[str, Thesis] = {}
    master_plans: Dict[str, MasterPlan] = {}
    projects: Dict[str, Project] = {}
    designs: Dict[str, Design] = {}
    actions: Dict[str, Action] = {}

    for entity_id, entity in entities.items():
        if isinstance(entity, Concept):
            concepts[entity.id] = entity
        elif isinstance(entity, Thesis):
            theses[entity.id] = entity
        elif isinstance(entity, MasterPlan):
            master_plans[entity.id] = entity
        elif isinstance(entity, Project):
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
    ]

    if concepts:
        lines.extend([
            "## Concepts",
            "",
            "| ID | Title | Type | Status |",
            "| --- | --- | --- | --- |",
        ])
        for cid, concept in sorted(concepts.items()):
            filename = id_to_filename.get(cid, f"{cid}-{concept.title.lower().replace(' ', '-')}.md")
            link = f"concepts/{filename}"
            lines.append(f"| [{cid}]({link}) | {concept.title} | {concept.concept_type.value} | {concept.status.value} |")
        lines.extend(["", "---", ""])

    if theses:
        lines.extend([
            "## Theses",
            "",
            "| ID | Title | Status | Conviction |",
            "| --- | --- | --- | --- |",
        ])
        for tid, thesis in sorted(theses.items()):
            filename = id_to_filename.get(tid, f"{tid}-{thesis.title.lower().replace(' ', '-')}.md")
            link = f"theses/{filename}"
            lines.append(f"| [{tid}]({link}) | {thesis.title} | {thesis.status.value} | {thesis.conviction} |")
        lines.extend(["", "---", ""])

    if master_plans:
        lines.extend([
            "## Master Plans",
            "",
            "| ID | Title | Status | Priority |",
            "| --- | --- | --- | --- |",
        ])
        for mid, mp in sorted(master_plans.items()):
            filename = id_to_filename.get(mid, f"{mid}-{mp.title.lower().replace(' ', '-')}.md")
            link = f"master_plans/{filename}"
            lines.append(f"| [{mid}]({link}) | {mp.title} | {mp.status.value} | {mp.priority.value} |")
        lines.extend(["", "---", ""])

    lines.extend([
        "## Projects",
        "",
        "| ID | Title | Status | Priority | Key Open Work |",
        "| --- | --- | --- | --- | --- |",
    ])

    for pid, project in sorted(projects.items()):
        first_task = "TBD"
        # Use actual filename if available, otherwise fall back to generated slug
        filename = id_to_filename.get(pid, f"{pid}-{project.title.lower().replace(' ', '-')}.md")
        link = f"projects/{filename}"

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
        # Use actual filename if available, otherwise fall back to generated slug
        filename = id_to_filename.get(did, f"{did}-{design.title.lower().replace(' ', '-')}.md")
        link = f"designs/{filename}"
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
        # Use actual filename if available, otherwise fall back to generated slug
        filename = id_to_filename.get(aid, f"{aid}-{action.title.lower().replace(' ', '-')}.md")
        link = f"actions/{filename}"
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
    # Build mapping of entity ID to actual filename by enumerating directories
    id_to_filename = {}
    for category in ["concepts", "theses", "master_plans", "projects", "designs", "actions"]:
        category_dir = plan_dir / category
        if not category_dir.exists():
            continue

        for filepath in category_dir.glob("*.md"):
            filename = filepath.name
            # Extract ID from filename (e.g., "P001-price-levels-strategy.md" → "P001")
            entity_id = filename.split('-')[0]
            id_to_filename[entity_id] = filename

    index_path = plan_dir / "INDEX.md"
    content = generate_index(entities, repo_name, id_to_filename)
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
