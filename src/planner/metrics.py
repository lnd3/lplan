"""Project metrics: fan-in, fan-out, depth, height, criticality."""

from typing import Dict, List, Set, Tuple
from .models import Project
from .graph import DependencyGraph


def compute_project_metrics(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> Dict:
    """Compute metrics for a single project.

    Args:
        project_id: Project ID
        projects: Dict of all projects
        graph: Dependency graph

    Returns:
        {
            'project_id': str,
            'fan_in': int,  # how many depend on this (direct)
            'fan_out': int,  # what does this depend on (direct)
            'depth': int,  # distance from root (no dependencies)
            'height': int,  # distance to leaf (no dependents)
            'criticality': float,  # score 0-1 (high = many depend on this)
        }
    """
    if project_id not in projects:
        raise ValueError(f"Project {project_id} not found")

    # Fan-in: projects that depend on this
    fan_in = len(list(graph.get_blocked_by(project_id)))

    # Fan-out: dependencies of this project
    fan_out = len(list(graph.get_blocking_deps(project_id)))

    # Depth: distance from a project with no dependencies (root)
    # Root projects have depth 0, their dependents have depth 1, etc.
    depth = _compute_depth(project_id, projects, graph)

    # Height: distance to a project with no dependents (leaf)
    # Leaf projects have height 0, their dependencies have height 1, etc.
    height = _compute_height(project_id, projects, graph)

    # Criticality: 0-1 score based on fan-in
    # More projects depend on you = higher criticality
    max_fan_in = max(
        len(list(graph.get_blocked_by(p))) for p in projects
    ) if projects else 1
    criticality = fan_in / max(max_fan_in, 1)

    return {
        "project_id": project_id,
        "title": projects[project_id].title,
        "fan_in": fan_in,
        "fan_out": fan_out,
        "depth": depth,
        "height": height,
        "criticality": round(criticality, 2),
    }


def compute_all_metrics(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> Dict[str, Dict]:
    """Compute metrics for all projects.

    Returns:
        Dict mapping project_id → metrics dict
    """
    return {
        project_id: compute_project_metrics(project_id, projects, graph)
        for project_id in projects
    }


def _compute_depth(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
    memo: Dict[str, int] = None,
) -> int:
    """Compute depth: distance from a root project (no dependencies)."""
    if memo is None:
        memo = {}

    if project_id in memo:
        return memo[project_id]

    dependencies = list(graph.get_blocking_deps(project_id))

    if not dependencies:
        depth = 0
    else:
        max_dep_depth = max(
            _compute_depth(dep, projects, graph, memo)
            for dep in dependencies
            if dep in projects
        )
        depth = max_dep_depth + 1

    memo[project_id] = depth
    return depth


def _compute_height(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
    memo: Dict[str, int] = None,
) -> int:
    """Compute height: distance to a leaf project (no dependents)."""
    if memo is None:
        memo = {}

    if project_id in memo:
        return memo[project_id]

    dependents = list(graph.get_blocked_by(project_id))

    if not dependents:
        height = 0
    else:
        max_dep_height = max(
            _compute_height(dep, projects, graph, memo)
            for dep in dependents
            if dep in projects
        )
        height = max_dep_height + 1

    memo[project_id] = height
    return height


def get_critical_path(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> Tuple[int, List[str]]:
    """Find the longest dependency chain (critical path).

    Returns:
        (chain_length, [project_ids in order from root to leaf])
    """
    if not projects:
        return 0, []

    longest_chain = []
    longest_length = 0

    # Start from each root project and follow the longest path
    for project_id in projects:
        chain = _build_longest_chain(project_id, projects, graph, set())
        if len(chain) > longest_length:
            longest_length = len(chain)
            longest_chain = chain

    return longest_length, longest_chain


def _build_longest_chain(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
    visited: set,
) -> List[str]:
    """Build longest chain starting from a project (avoiding cycles)."""
    if project_id in visited:
        return [project_id]

    visited.add(project_id)

    dependents = [
        d for d in graph.get_blocked_by(project_id)
        if d in projects and d not in visited
    ]

    if not dependents:
        return [project_id]

    longest = [project_id]
    for dependent in dependents:
        chain = _build_longest_chain(dependent, projects, graph, visited.copy())
        if len(chain) + 1 > len(longest):
            longest = [project_id] + chain

    return longest
