"""Hierarchy-wide rollups and "needs attention" signals for the Plan Health Dashboard.

Pure functions: plan data in, dicts out. No Flask, no I/O beyond what's already
been parsed by the caller — mirrors metrics.py/impact.py/bottleneck.py.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from .graph import DependencyGraph
from .models import Action, Concept, Design, MasterPlan, PlanFile, Project, Thesis
from .parser import count_checkboxes
from .refs import check_references
from .validator import SchemaValidator

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


def _rollup_pct(
    entity_status: str, done_children: int, total_children: int, plan_file: Optional[PlanFile],
) -> Dict[str, Any]:
    """Shared rollup-percentage logic for Projects and Master Plans.

    Prefer the entity's own Tasks/Phases checkboxes over child-entity counts:
    the child set grows as work gets discovered mid-flight (mostly upward,
    rarely downward), so "% of children DONE" drifts in ways that don't
    reflect actual progress. Checkboxes are the human's deliberate plan of
    record instead — checked off on purpose, not as a side effect of scope
    discovery. Child counts remain in the payload as informational context,
    they just don't drive `pct_done` when a better signal is available.
    """
    checkbox_done, checkbox_total = count_checkboxes(plan_file.raw_content) if plan_file else (0, 0)

    if checkbox_total:
        pct = round(100 * checkbox_done / checkbox_total)
        source = "checkboxes"
    elif total_children:
        pct = round(100 * done_children / total_children)
        source = "children"
    else:
        pct = 100 if entity_status == "DONE" else 0
        source = "status"

    return {
        "pct_done": pct,
        "pct_source": source,
        "checkbox_done": checkbox_done,
        "checkbox_total": checkbox_total,
    }


def project_rollup(
    project: Project, designs: Dict[str, Design], actions: Dict[str, Action],
    path_by_id: Optional[Dict[str, str]] = None,
    plan_file: Optional[PlanFile] = None,
) -> Dict[str, Any]:
    """Progress for a project: prefers its own Tasks/Phases checkboxes, falls back
    to % of directly-tagged Designs + Actions that are DONE. See `_rollup_pct`."""
    children = [d for d in designs.values() if d.project == project.id]
    children += [a for a in actions.values() if a.project == project.id]

    total = len(children)
    done = sum(1 for c in children if c.status == "DONE")

    return {
        "id": project.id,
        "title": project.title,
        "status": project.status,
        "path": (path_by_id or {}).get(project.id),
        "child_count": total,
        "child_done": done,
        "no_children": total == 0,
        **_rollup_pct(project.status, done, total, plan_file),
    }


def master_plan_rollup(
    master_plan: MasterPlan, projects: Dict[str, Project],
    path_by_id: Optional[Dict[str, str]] = None,
    plan_file: Optional[PlanFile] = None,
) -> Dict[str, Any]:
    """Progress for a master plan: prefers its own Tasks/Phases checkboxes, falls
    back to % of child Projects (via parent_master_plan) that are DONE."""
    children = [p for p in projects.values() if master_plan.id in (p.parent_master_plan or [])]

    total = len(children)
    done = sum(1 for c in children if c.status == "DONE")

    return {
        "id": master_plan.id,
        "title": master_plan.title,
        "status": master_plan.status,
        "path": (path_by_id or {}).get(master_plan.id),
        "child_count": total,
        "child_done": done,
        "no_projects_yet": total == 0,
        **_rollup_pct(master_plan.status, done, total, plan_file),
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


def collect_validator_warnings(
    entities_by_id: Dict[str, Any],
    projects: Dict[str, Project],
    plan_files_by_id: Dict[str, PlanFile],
    path_by_id: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Run the full SchemaValidator and surface its warnings in the dashboard.

    Before this, the needs-attention panel only pulled from check_references()
    (dangling refs) — entity/relationship-level warnings from `plan validate`
    (e.g. A027's DONE-parent-with-open-children check, D008's unanchored-phase
    check) were invisible here even though the CLI showed them. This closes
    that gap by running the same validator the CLI uses.
    """
    validator = SchemaValidator()
    for entity in entities_by_id.values():
        validator.validate_entity(entity)
    validator.validate_relationships(entities_by_id)

    raw_content_by_project_id = {
        pid: plan_files_by_id[pid].raw_content
        for pid in projects
        if pid in plan_files_by_id
    }
    validator.validate_phase_anchors(raw_content_by_project_id, entities_by_id)

    type_names = {
        Concept: "concept", Thesis: "thesis", MasterPlan: "master_plan",
        Project: "project", Design: "design", Action: "action",
    }
    path_by_id = path_by_id or {}

    results = []
    for w in validator.warnings:
        entity = entities_by_id.get(w.entity_id)
        results.append({
            "id": w.entity_id,
            "type": type_names.get(type(entity), "unknown"),
            "field": w.field,
            "message": w.message,
            "path": path_by_id.get(w.entity_id),
        })
    return results


def dangling_references(entities_by_id: Dict[str, Any], plan_dir) -> Dict[str, Any]:
    """Wraps refs.check_references — same code path as `plan check-refs`."""
    report = check_references(entities_by_id, plan_dir)
    return {
        "orphaned_designs": report["orphaned_designs"],
        "orphaned_actions": report["orphaned_actions"],
        "unused_projects": report["unused_projects"],
        "unresolvable_refs": report["unresolvable_refs"],
        "dead_companion_links": report["dead_companion_links"],
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

    # Least-complete first, most-complete last — surfaces what needs work
    # before what's already finished. Sort by (id) as a stable tiebreaker so
    # equal-progress rows don't reorder from one request to the next.
    master_plan_rollups = sorted(
        (master_plan_rollup(mp, projects, path_by_id, plan_files_by_id.get(mp.id))
         for mp in master_plans.values()),
        key=lambda r: (r["pct_done"], r["id"]),
    )
    project_rollups = sorted(
        (project_rollup(p, designs, actions, path_by_id, plan_files_by_id.get(p.id))
         for p in projects.values()),
        key=lambda r: (r["pct_done"], r["id"]),
    )

    return {
        "totals": overall_totals(concepts, theses, master_plans, projects, designs, actions),
        "master_plan_rollups": master_plan_rollups,
        "project_rollups": project_rollups,
        "needs_attention": {
            "stale": find_stale(entities_by_type, plan_files_by_id, today, stale_days, path_by_id),
            "blocked": find_blocked(entities_by_type, graph, path_by_id),
            "dangling_references": dangling_references(entities_by_id, plan_dir),
            "validator_warnings": collect_validator_warnings(entities_by_id, projects, plan_files_by_id, path_by_id),
        },
        "stale_days_threshold": stale_days,
    }
