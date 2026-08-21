"""Impact analysis: what unblocks when a project completes."""

from typing import Dict, List, Set
from .models import Project
from .graph import DependencyGraph


def analyze_impact(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> Dict:
    """Analyze impact of completing a project.

    Returns:
        {
            'project_id': str,
            'title': str,
            'unblocks': [project_ids],  # projects that depend on this
            'blocked_by': [project_ids],  # dependencies of this project
            'downstream': [project_ids],  # transitive dependents
            'upstream': [project_ids],  # transitive dependencies
            'num_unblocked': int,  # count of directly unblocked
            'num_downstream': int,  # count of downstream impact
            'impact_ratio': float,  # downstream / (status coverage)
        }
    """
    if project_id not in projects:
        raise ValueError(f"Project {project_id} not found")

    project = projects[project_id]

    # Direct unblocks (projects that depend on this one)
    unblocks = list(graph.get_blocked_by(project_id))

    # Dependencies (what blocks this)
    blocked_by = list(graph.get_blocking_deps(project_id))

    # Transitive dependents (full downstream impact)
    downstream: Set[str] = set()
    for unblocked_id in unblocks:
        downstream.update(graph.get_blocked_by(unblocked_id))

    # Transitive dependencies (what we depend on)
    upstream = list(graph.get_transitive_deps(project_id))

    # Impact ratio: how much of the graph depends on this (directly or indirectly)
    total_projects = len(projects)
    impact_count = len({project_id, *unblocks, *downstream})
    impact_ratio = impact_count / total_projects if total_projects > 0 else 0.0

    return {
        "project_id": project_id,
        "title": project.title,
        "status": project.status.value,
        "unblocks": unblocks,
        "blocked_by": blocked_by,
        "downstream": list(downstream),
        "upstream": upstream,
        "num_unblocked": len(unblocks),
        "num_downstream": len(downstream),
        "impact_ratio": round(impact_ratio, 2),
    }


def get_most_impactful_projects(
    projects: Dict[str, Project],
    graph: DependencyGraph,
    limit: int = 5,
) -> List[Dict]:
    """Find projects with highest impact (most unblocked downstream).

    Args:
        projects: Dict of projects
        graph: Dependency graph
        limit: Number to return

    Returns:
        List of impact analysis dicts, sorted by impact_ratio descending
    """
    impacts = []
    for project_id in projects:
        try:
            impact = analyze_impact(project_id, projects, graph)
            impacts.append(impact)
        except ValueError:
            pass

    # Sort by impact_ratio, then by num_downstream
    impacts.sort(key=lambda x: (x["impact_ratio"], x["num_downstream"]), reverse=True)
    return impacts[:limit]
