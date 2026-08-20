"""Statistics and analytics for planning data."""

from collections import defaultdict
from datetime import date
from typing import Dict, List, Tuple, Optional
from .models import PlanEntity, Project, Design, Action, Status
from .priority import PriorityEngine
from .graph import DependencyGraph


def compute_stats(entities: Dict[str, PlanEntity]) -> Dict[str, any]:
    """Compute aggregate statistics across all entities.

    Args:
        entities: Dict of all entities

    Returns:
        Dict with keys:
        - projects_total, designs_total, actions_total: Entity counts
        - by_status: {status -> count}
        - by_priority: {priority -> count} (projects only)
        - percent_done: % of projects that are DONE
        - blocked_count: Count of BLOCKED projects
        - priority_mismatches: Count of projects where computed != declared priority
    """
    stats: Dict[str, any] = {
        "projects_total": 0,
        "designs_total": 0,
        "actions_total": 0,
        "by_status": defaultdict(int),
        "by_priority": defaultdict(int),
        "percent_done": 0.0,
        "blocked_count": 0,
        "priority_mismatches": 0,
    }

    projects: Dict[str, Project] = {}
    all_entities: Dict[str, PlanEntity] = {}

    for eid, entity in entities.items():
        all_entities[eid] = entity
        if isinstance(entity, Project):
            projects[entity.id] = entity
            stats["projects_total"] += 1
            stats["by_priority"][entity.priority.value] += 1
        elif isinstance(entity, Design):
            stats["designs_total"] += 1
        elif isinstance(entity, Action):
            stats["actions_total"] += 1

        stats["by_status"][entity.status.value] += 1

    # Compute percent done (projects)
    if projects:
        done_count = sum(1 for p in projects.values() if p.status == Status.DONE)
        stats["percent_done"] = 100.0 * done_count / len(projects)

    # Count blocked
    stats["blocked_count"] = sum(1 for e in all_entities.values() if e.status == Status.BLOCKED)

    # Check priority mismatches
    engine = PriorityEngine()
    mismatches = 0
    for project in projects.values():
        analysis = engine.analyze_project(project)
        if not analysis.get("match"):
            mismatches += 1
    stats["priority_mismatches"] = mismatches

    return stats


def compute_timeline(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> List[Tuple[int, List[str]]]:
    """Compute execution phases for projects.

    Projects with no dependencies are phase 0. Each subsequent phase
    contains projects whose direct dependencies are all in earlier phases.

    Args:
        projects: Dict of all projects
        graph: Dependency graph

    Returns:
        List of (phase_number, [project_ids]) tuples, in order
    """
    phases: Dict[int, List[str]] = defaultdict(list)
    memo: Dict[str, int] = {}

    def compute_level(project_id: str) -> int:
        """Compute phase level for a project (memoized)."""
        if project_id in memo:
            return memo[project_id]

        # Get blocking dependencies
        blocking_deps = graph.get_blocking_deps(project_id)

        if not blocking_deps:
            # No dependencies, phase 0
            level = 0
        else:
            # Phase = 1 + max(phase of all dependencies)
            max_dep_level = max(compute_level(dep) for dep in blocking_deps if dep in projects)
            level = max_dep_level + 1

        memo[project_id] = level
        return level

    # Compute level for all projects
    for project_id in projects:
        level = compute_level(project_id)
        phases[level].append(project_id)

    # Return as sorted list of tuples
    return sorted((level, ids) for level, ids in phases.items())


def compute_estimates(projects: Dict[str, Project]) -> Dict[str, any]:
    """Compute time estimate rollup.

    Args:
        projects: Dict of all projects

    Returns:
        Dict with keys:
        - total_effort_days: Sum of all effort_days
        - projects_with_estimates: Count
        - projects_without_estimates: Count
        - by_status: {status -> (total_days, project_count)}
    """
    stats: Dict[str, any] = {
        "total_effort_days": 0.0,
        "projects_with_estimates": 0,
        "projects_without_estimates": 0,
        "by_status": defaultdict(lambda: (0.0, 0)),
    }

    for project in projects.values():
        if project.estimate and project.estimate.effort_days:
            stats["total_effort_days"] += project.estimate.effort_days
            stats["projects_with_estimates"] += 1

            # Accumulate by status
            status = project.status.value
            current_days, current_count = stats["by_status"][status]
            stats["by_status"][status] = (
                current_days + project.estimate.effort_days,
                current_count + 1,
            )
        else:
            stats["projects_without_estimates"] += 1

    # Convert defaultdict to regular dict for cleaner output
    stats["by_status"] = dict(stats["by_status"])

    return stats


def compute_velocity(projects: Dict[str, Project]) -> Dict[str, any]:
    """Compute velocity metrics from completed estimates.

    For projects with both started and completed dates + effort_days,
    compute actual duration vs estimated and average variance.

    Args:
        projects: Dict of all projects

    Returns:
        Dict with keys:
        - completed_projects: Count of DONE with both dates + estimate
        - average_variance_percent: % (actual - estimated) / estimated, averaged
        - projects: List of {id, title, effort_days, actual_days, variance_percent}
        - incomplete_estimates: Count of DONE projects missing estimate data
    """
    stats: Dict[str, any] = {
        "completed_projects": 0,
        "average_variance_percent": 0.0,
        "projects": [],
        "incomplete_estimates": 0,
    }

    completed_with_data = []

    for project in projects.values():
        if project.status != Status.DONE:
            continue

        # Check if estimate exists with all required fields
        if not project.estimate:
            stats["incomplete_estimates"] += 1
            continue

        if not (project.estimate.effort_days and project.estimate.started and project.estimate.completed):
            stats["incomplete_estimates"] += 1
            continue

        # Compute actual duration
        actual_days = (project.estimate.completed - project.estimate.started).days
        effort_days = project.estimate.effort_days

        # Variance: (actual - estimated) / estimated * 100
        variance_percent = 100.0 * (actual_days - effort_days) / effort_days

        stats["projects"].append({
            "id": project.id,
            "title": project.title,
            "effort_days": effort_days,
            "actual_days": actual_days,
            "variance_percent": round(variance_percent, 1),
        })

        completed_with_data.append(variance_percent)

    # Compute average variance
    if completed_with_data:
        stats["completed_projects"] = len(completed_with_data)
        stats["average_variance_percent"] = round(sum(completed_with_data) / len(completed_with_data), 1)

    return stats
