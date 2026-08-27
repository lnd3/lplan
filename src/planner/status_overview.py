"""Hierarchy-wide rollups and "needs attention" signals for the Plan Health Dashboard.

Pure functions: plan data in, dicts out. No Flask, no I/O beyond what's already
been parsed by the caller — mirrors metrics.py/impact.py/bottleneck.py.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from .graph import DependencyGraph
from .models import Action, Concept, Design, MasterPlan, PlanFile, Project, Thesis
from .refs import check_references

DEFAULT_STALE_DAYS = 3


def _entry_date(log_line: str) -> Optional[date]:
    """Parse the leading YYYY-MM-DD off a '## Log' line, if present."""
    prefix = log_line[:10]
    try:
        y, m, d = (int(part) for part in prefix.split("-"))
        return date(y, m, d)
    except (ValueError, IndexError):
        return None


def _last_activity(entity, plan_file: Optional[PlanFile]) -> date:
    """Most recent of `updated` and the newest '## Log' entry date."""
    last = entity.updated
    if plan_file and plan_file.log:
        for line in plan_file.log:
            d = _entry_date(line)
            if d and d > last:
                last = d
    return last


def project_rollup(
    project: Project, designs: Dict[str, Design], actions: Dict[str, Action],
    path_by_id: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """% of a project's directly-tagged Designs + Actions that are DONE."""
    children = [d for d in designs.values() if d.project == project.id]
    children += [a for a in actions.values() if a.project == project.id]

    total = len(children)
    done = sum(1 for c in children if c.status == "DONE")
    pct = round(100 * done / total) if total else (100 if project.status == "DONE" else 0)

    return {
        "id": project.id,
        "title": project.title,
        "status": project.status,
        "path": (path_by_id or {}).get(project.id),
        "child_count": total,
        "child_done": done,
        "pct_done": pct,
        "no_children": total == 0,
    }


def master_plan_rollup(
    master_plan: MasterPlan, projects: Dict[str, Project],
    path_by_id: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """% of a master plan's child Projects (via parent_master_plan) that are DONE."""
    children = [p for p in projects.values() if master_plan.id in (p.parent_master_plan or [])]

    total = len(children)
    done = sum(1 for c in children if c.status == "DONE")
    pct = round(100 * done / total) if total else 0

    return {
        "id": master_plan.id,
        "title": master_plan.title,
        "status": master_plan.status,
        "path": (path_by_id or {}).get(master_plan.id),
        "child_count": total,
        "child_done": done,
        "pct_done": pct,
        "no_projects_yet": total == 0,
    }


def overall_totals(
    concepts: Dict[str, Concept],
    theses: Dict[str, Thesis],
    master_plans: Dict[str, MasterPlan],
    projects: Dict[str, Project],
    designs: Dict[str, Design],
    actions: Dict[str, Action],
) -> Dict[str, Dict[str, int]]:
    """Status counts per entity type, e.g. {"project": {"DONE": 6, "IN_PROGRESS": 2, ...}}."""
    groups = {
        "concept": concepts,
        "thesis": theses,
        "master_plan": master_plans,
        "project": projects,
        "design": designs,
        "action": actions,
    }
    totals: Dict[str, Dict[str, int]] = {}
    for type_name, entities in groups.items():
        counts: Dict[str, int] = {}
        for entity in entities.values():
            counts[entity.status] = counts.get(entity.status, 0) + 1
        totals[type_name] = counts
    return totals


def find_stale(
    entities_by_type: Dict[str, Dict[str, Any]],
    plan_files_by_id: Dict[str, PlanFile],
    today: date,
    stale_days: int = DEFAULT_STALE_DAYS,
    path_by_id: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """IN_PROGRESS entities with no updated/Log activity in `stale_days` days."""
    stale = []
    for type_name, entities in entities_by_type.items():
        for entity in entities.values():
            if entity.status != "IN_PROGRESS":
                continue
            last_active = _last_activity(entity, plan_files_by_id.get(entity.id))
            days = (today - last_active).days
            if days >= stale_days:
                stale.append({
                    "id": entity.id,
                    "title": entity.title,
                    "type": type_name,
                    "path": (path_by_id or {}).get(entity.id),
                    "days_since_activity": days,
                    "last_activity": last_active.isoformat(),
                })
    stale.sort(key=lambda e: -e["days_since_activity"])
    return stale


def find_blocked(
    entities_by_type: Dict[str, Dict[str, Any]],
    graph: DependencyGraph,
    path_by_id: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """BLOCKED entities. Blocker detail is only available for Projects (dependency graph)."""
    blocked = []
    for type_name, entities in entities_by_type.items():
        for entity in entities.values():
            if entity.status != "BLOCKED":
                continue
            blockers: List[str] = []
            if type_name == "project":
                try:
                    blockers = [
                        dep for dep in graph.get_blocking_deps(entity.id)
                    ]
                except Exception:
                    blockers = []
            blocked.append({
                "id": entity.id,
                "title": entity.title,
                "type": type_name,
                "path": (path_by_id or {}).get(entity.id),
                "blockers": blockers,
            })
    return blocked


def dangling_references(entities_by_id: Dict[str, Any], plan_dir) -> Dict[str, Any]:
    """Wraps refs.check_references — same code path as `plan check-refs`."""
    report = check_references(entities_by_id, plan_dir)
    return {
        "orphaned_designs": report["orphaned_designs"],
        "orphaned_actions": report["orphaned_actions"],
        "unused_projects": report["unused_projects"],
        "unresolvable_refs": report["unresolvable_refs"],
    }


def compute_status_overview(
    concepts: Dict[str, Concept],
    theses: Dict[str, Thesis],
    master_plans: Dict[str, MasterPlan],
    projects: Dict[str, Project],
    designs: Dict[str, Design],
    actions: Dict[str, Action],
    plan_files_by_id: Dict[str, PlanFile],
    graph: DependencyGraph,
    plan_dir,
    path_by_id: Optional[Dict[str, str]] = None,
    stale_days: int = DEFAULT_STALE_DAYS,
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """Assemble the full /api/status-overview payload."""
    today = today or date.today()
    path_by_id = path_by_id or {}

    entities_by_type = {
        "concept": concepts,
        "thesis": theses,
        "master_plan": master_plans,
        "project": projects,
        "design": designs,
        "action": actions,
    }
    entities_by_id: Dict[str, Any] = {}
    for group in entities_by_type.values():
        entities_by_id.update(group)

    return {
        "totals": overall_totals(concepts, theses, master_plans, projects, designs, actions),
        "master_plan_rollups": [
            master_plan_rollup(mp, projects, path_by_id) for mp in sorted(master_plans.values(), key=lambda x: x.id)
        ],
        "project_rollups": [
            project_rollup(p, designs, actions, path_by_id) for p in sorted(projects.values(), key=lambda x: x.id)
        ],
        "needs_attention": {
            "stale": find_stale(entities_by_type, plan_files_by_id, today, stale_days, path_by_id),
            "blocked": find_blocked(entities_by_type, graph, path_by_id),
            "dangling_references": dangling_references(entities_by_id, plan_dir),
        },
        "stale_days_threshold": stale_days,
    }
