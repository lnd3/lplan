"""Index and changelog generation for plan visibility."""

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from .models import PlanEntity, Project, Design, Action, Thesis, MasterPlan, Concept

# D008: severity ordering for a phase's "worst-case child status" (lower = worse)
_PHASE_STATUS_SEVERITY = {
    "BLOCKED": 0, "IN_PROGRESS": 1, "PLANNING": 2, "IDEA": 3,
    "DEFERRED": 4, "CANCELLED": 5, "DONE": 6,
}


def _collect_phase_summaries(entities: Dict[str, PlanEntity]) -> Dict[str, Dict[str, dict]]:
    """D008: group Designs/Actions carrying a `phase` field by (project, phase name).

    Returns {project_id: {phase_name: {"designs": [ids], "actions": [ids], "status": worst_status}}}
    """

    def action_project(action: Action) -> Optional[str]:
        if action.project:
            return action.project
        if action.design and action.design in entities:
            parent = entities[action.design]
            if isinstance(parent, Design):
                return parent.project
        return None

    raw: Dict[str, Dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"designs": [], "actions": [], "statuses": []}))

    for entity in entities.values():
        if isinstance(entity, Design) and entity.phase:
            bucket = raw[entity.project][entity.phase]
            bucket["designs"].append(entity.id)
            bucket["statuses"].append(entity.status.value)
        elif isinstance(entity, Action) and entity.phase:
            project_id = action_project(entity)
            if not project_id:
                continue
            bucket = raw[project_id][entity.phase]
            bucket["actions"].append(entity.id)
            bucket["statuses"].append(entity.status.value)

    result: Dict[str, Dict[str, dict]] = {}
    for project_id, phases in raw.items():
        result[project_id] = {}
        for phase_name, bucket in phases.items():
            worst = min(bucket["statuses"], key=lambda s: _PHASE_STATUS_SEVERITY.get(s, 99))
            result[project_id][phase_name] = {
                "designs": sorted(bucket["designs"]),
                "actions": sorted(bucket["actions"]),
                "status": worst,
            }
    return result


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
    companions_by_id: Dict[str, List[str]] = None,
    include_companions: bool = False,
) -> str:
    """Generate INDEX.md markdown.

    Args:
        entities: Dict mapping entity IDs to PlanEntity objects
        repo_name: Name of the repository (used in heading)
        id_to_filename: Dict mapping entity ID to actual filename (e.g., "P001" → "P001-price-levels-strategy.md")
        companions_by_id: Dict mapping entity ID to its D005 companion filenames (see companions.py).
            Companions never appear as their own table rows — only as a "see also" note on
            their root entity's row.
        include_companions: If True, append a trailing "## Companions" inventory section.

    Returns:
        Markdown string ready to write to INDEX.md
    """
    if id_to_filename is None:
        id_to_filename = {}
    if companions_by_id is None:
        companions_by_id = {}

    def see_also(entity_id: str) -> str:
        names = companions_by_id.get(entity_id)
        if not names:
            return ""
        return " 📎 _see also: " + ", ".join(f"`{n}`" for n in names) + "_"

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
            lines.append(f"| [{cid}]({link}) | {concept.title}{see_also(cid)} | {concept.concept_type.value} | {concept.status.value} |")
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
            lines.append(f"| [{tid}]({link}) | {thesis.title}{see_also(tid)} | {thesis.status.value} | {thesis.conviction} |")
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
            lines.append(f"| [{mid}]({link}) | {mp.title}{see_also(mid)} | {mp.status.value} | {mp.priority.value} |")
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

        lines.append(f"| [{pid}]({link}) | {project.title}{see_also(pid)} | {project.status.value} | {project.priority.value} | {first_task} |")

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
        lines.append(f"| [{did}]({link}) | {design.title}{see_also(did)} | {design.status.value} | {project_ref} | (link if applicable) |")

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
        lines.append(f"| [{aid}]({link}) | {action.title}{see_also(aid)} | {action.status.value} | {design_ref} | TBD |")

    phase_summaries = _collect_phase_summaries(entities)
    if phase_summaries:
        lines.extend(["", "---", "", "## Phase Summaries", "", "*D008: supplementary view built from children's `phase` fields — the project file's own Phases text stays authoritative.*", ""])
        for project_id in sorted(phase_summaries):
            project_title = entities[project_id].title if project_id in entities else project_id
            lines.extend([f"### {project_id} — {project_title}", "", "| Phase | Designs | Actions | Status |", "| --- | --- | --- | --- |"])
            for phase_name in sorted(phase_summaries[project_id]):
                info = phase_summaries[project_id][phase_name]
                designs_cell = ", ".join(info["designs"]) or "—"
                actions_cell = ", ".join(info["actions"]) or "—"
                lines.append(f"| {phase_name} | {designs_cell} | {actions_cell} | {info['status']} |")
            lines.append("")

    if include_companions and companions_by_id:
        lines.extend(["", "---", "", "## Companions", "", "| Root | Companion files |", "| --- | --- |"])
        for entity_id in sorted(companions_by_id):
            names = ", ".join(f"`{n}`" for n in companions_by_id[entity_id])
            lines.append(f"| {entity_id} | {names} |")

    return "\n".join(lines)


def write_index(
    plan_dir: Path,
    entities: Dict[str, PlanEntity],
    repo_name: str = "Plan",
    include_companions: bool = False,
) -> Path:
    """Write INDEX.md to plan directory.

    Args:
        plan_dir: Path to plan directory
        entities: Dict of entities to include
        repo_name: Name for the index heading
        include_companions: If True, append a trailing "## Companions" inventory section

    Returns:
        Path to written INDEX.md
    """
    from .companions import companion_root_stem, is_companion_file

    # Build mapping of entity ID to actual filename by enumerating directories.
    # Companion files (D005) are skipped here — they're not entities and don't
    # get their own row; they're surfaced as a "see also" note on their root instead.
    id_to_filename: Dict[str, str] = {}
    companions_by_id: Dict[str, List[str]] = {}
    for category in ["concepts", "theses", "master_plans", "projects", "designs", "actions"]:
        category_dir = plan_dir / category
        if not category_dir.exists():
            continue

        for filepath in category_dir.glob("*.md"):
            if is_companion_file(filepath):
                companions_by_id.setdefault(companion_root_stem(filepath), []).append(filepath.name)
                continue
            filename = filepath.name
            # Extract ID from filename (e.g., "P001-price-levels-strategy.md" → "P001")
            entity_id = filename.split('-')[0]
            id_to_filename[entity_id] = filename

    for name in list(companions_by_id):
        companions_by_id[name].sort()

    index_path = plan_dir / "INDEX.md"
    content = generate_index(entities, repo_name, id_to_filename, companions_by_id, include_companions)
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
