"""Capacity analysis: estimates vs timeline, parallelization opportunities."""

from typing import Dict, List, Tuple
from .models import Project, Status
from .graph import DependencyGraph
from .stats import compute_timeline


def analyze_capacity(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> Dict:
    """Analyze capacity and identify parallelization opportunities.

    Returns:
        {
            'total_effort_days': float,
            'estimated_projects': int,
            'unestimated_projects': int,
            'by_status': {status -> {effort_days, count}},
            'critical_path_days': int,
            'parallelizable_effort': float,
            'timeline_phases': [(phase, projects, ideal_days)],
            'compression_ratio': float,
        }
    """
    if not projects:
        return {
            "total_effort_days": 0.0,
            "estimated_projects": 0,
            "unestimated_projects": 0,
            "by_status": {},
            "critical_path_days": 0,
            "parallelizable_effort": 0.0,
            "timeline_phases": [],
            "compression_ratio": 1.0,
        }

    # Compute timeline phases
    timeline = compute_timeline(projects, graph)

    # Compute metrics for each phase
    timeline_phases = []
    critical_path_days = 0
    total_effort = 0.0
    estimated_count = 0

    for phase_num, project_ids in timeline:
        phase_effort = 0.0
        phase_count = 0

        for pid in project_ids:
            if pid in projects:
                project = projects[pid]
                if project.estimate and project.estimate.effort_days:
                    phase_effort += project.estimate.effort_days
                    estimated_count += 1
                total_effort += project.estimate.effort_days if project.estimate else 0

        phase_count = len([p for p in project_ids if p in projects])

        # In a phase, projects run in parallel, so phase duration = max (not sum)
        phase_duration = phase_effort / len(project_ids) if project_ids else 0

        critical_path_days += phase_duration
        timeline_phases.append({
            "phase": phase_num,
            "projects": project_ids,
            "project_count": phase_count,
            "total_effort_days": round(phase_effort, 1),
            "ideal_duration_days": round(phase_duration, 1),
        })

    # Count by status
    by_status = {}
    for project in projects.values():
        status = project.status.value
        if status not in by_status:
            by_status[status] = {"effort_days": 0.0, "count": 0}

        if project.estimate and project.estimate.effort_days:
            by_status[status]["effort_days"] += project.estimate.effort_days

        by_status[status]["count"] += 1

    # Parallelizable: total - critical path
    parallelizable = max(0, total_effort - critical_path_days)

    # Compression ratio: how much can we compress with perfect parallelization
    compression_ratio = (
        total_effort / critical_path_days
        if critical_path_days > 0
        else 1.0
    )

    return {
        "total_effort_days": round(total_effort, 1),
        "estimated_projects": estimated_count,
        "unestimated_projects": len(projects) - estimated_count,
        "by_status": by_status,
        "critical_path_days": round(critical_path_days, 1),
        "parallelizable_effort": round(parallelizable, 1),
        "timeline_phases": timeline_phases,
        "compression_ratio": round(compression_ratio, 2),
    }


def suggest_parallelization(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> List[str]:
    """Suggest opportunities to parallelize work.

    Returns:
        List of suggestions like "P002 and P003 can run in parallel"
    """
    suggestions = []

    timeline = compute_timeline(projects, graph)

    # Look for phases with multiple projects (already parallel)
    # and phases with 1 project that could potentially be split

    for phase_num, project_ids in timeline:
        if len(project_ids) > 1:
            project_titles = [
                projects[p].title for p in project_ids if p in projects
            ]
            suggestions.append(
                f"Phase {phase_num}: {len(project_ids)} projects can run in parallel: "
                + ", ".join(project_titles[:3])
                + ("..." if len(project_titles) > 3 else "")
            )

    if not suggestions:
        suggestions.append("All work is sequential. Consider breaking dependencies.")

    return suggestions


def estimate_completion_date(
    projects: Dict[str, Project],
    graph: DependencyGraph,
    start_date = None,
) -> Tuple[str, str]:
    """Estimate project completion date based on critical path.

    Args:
        projects: Dict of projects
        graph: Dependency graph
        start_date: Assumed start date (default: today)

    Returns:
        (iso_date_string, human_readable_description)
    """
    from datetime import date, timedelta

    if start_date is None:
        start_date = date.today()
    elif isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    capacity = analyze_capacity(projects, graph)
    critical_path = capacity["critical_path_days"]

    if critical_path == 0:
        return (
            start_date.isoformat(),
            "No estimated work."
        )

    completion = start_date + timedelta(days=critical_path)

    description = (
        f"Estimated completion: {completion.isoformat()} "
        f"({int(critical_path)} days critical path with {len(projects)} projects)"
    )

    return completion.isoformat(), description
