"""Bottleneck detection: identify projects that block progress."""

from typing import Dict, List
from .models import Project, Status
from .graph import DependencyGraph
from .metrics import compute_all_metrics


def detect_bottlenecks(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> Dict:
    """Detect bottleneck projects that block many others.

    Returns:
        {
            'blocking_bottlenecks': [
                {
                    'project_id': str,
                    'title': str,
                    'status': str,
                    'unblocks': int,
                    'reason': str (why it's a bottleneck)
                }
            ],
            'deep_chains': [
                {
                    'length': int,
                    'chain': [project_ids],
                    'risk': str (description)
                }
            ],
            'summary': str,
        }
    """
    metrics = compute_all_metrics(projects, graph)

    # Find projects with high fan-in that are NOT DONE
    blocking_bottlenecks = []
    for project_id, metric in metrics.items():
        project = projects[project_id]
        fan_in = metric["fan_in"]

        # A bottleneck is: (1) not done, (2) multiple things depend on it
        if project.status != Status.DONE and fan_in >= 2:
            reason = f"Blocking {fan_in} other project(s)"
            if project.status == Status.BLOCKED:
                reason += " (AND is itself BLOCKED!)"

            blocking_bottlenecks.append({
                "project_id": project_id,
                "title": project.title,
                "status": project.status.value,
                "unblocks": fan_in,
                "reason": reason,
            })

    # Sort by unblocks (most impactful first)
    blocking_bottlenecks.sort(key=lambda x: x["unblocks"], reverse=True)

    # Find deep dependency chains (risk of schedule overruns)
    deep_chains = []
    if projects:
        for project_id in projects:
            chain = _find_longest_chain_from(project_id, projects, graph)
            if len(chain) >= 3:  # Chains of 3+ are concerning
                # Estimate total effort
                effort = sum(
                    (projects[p].estimate.effort_days or 0)
                    for p in chain
                    if projects[p].estimate
                )
                deep_chains.append({
                    "length": len(chain),
                    "chain": chain,
                    "effort_days": round(effort, 1),
                    "risk": f"Sequential dependency chain of {len(chain)} projects",
                })

        # Sort by length (longest/riskiest first)
        deep_chains.sort(key=lambda x: x["length"], reverse=True)

    # Generate summary
    summary = _generate_bottleneck_summary(blocking_bottlenecks, deep_chains)

    return {
        "blocking_bottlenecks": blocking_bottlenecks,
        "deep_chains": deep_chains,
        "summary": summary,
    }


def _find_longest_chain_from(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
    visited: set = None,
) -> List[str]:
    """Find longest dependency chain starting from a project."""
    if visited is None:
        visited = set()

    if project_id in visited or project_id not in projects:
        return [project_id]

    visited.add(project_id)

    # Find projects that depend on this one
    dependents = [
        d for d in graph.get_blocked_by(project_id)
        if d in projects and d not in visited
    ]

    if not dependents:
        return [project_id]

    longest = [project_id]
    for dependent in dependents:
        chain = _find_longest_chain_from(dependent, projects, graph, visited.copy())
        if len(chain) + 1 > len(longest):
            longest = [project_id] + chain

    return longest


def _generate_bottleneck_summary(
    blocking_bottlenecks: List[Dict],
    deep_chains: List[Dict],
) -> str:
    """Generate human-readable summary of bottlenecks."""
    issues = []

    if not blocking_bottlenecks and not deep_chains:
        return "✓ No critical bottlenecks detected."

    if blocking_bottlenecks:
        counts = {}
        for b in blocking_bottlenecks:
            status = b["status"]
            counts[status] = counts.get(status, 0) + 1

        if counts.get("BLOCKED"):
            issues.append(f"⚠ {counts['BLOCKED']} BLOCKED project(s) that block others!")
        if counts.get("PLANNING"):
            issues.append(f"⚠ {counts['PLANNING']} PLANNING project(s) blocking multiple others")

    if deep_chains:
        longest = deep_chains[0]
        issues.append(
            f"⚠ Longest dependency chain: {longest['length']} projects "
            f"({longest['effort_days']} days estimated)"
        )

    return " ".join(issues) if issues else "No critical issues."


def get_blockers_for(
    project_id: str,
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> List[Dict]:
    """Get all projects that block a specific project (direct + transitive).

    Returns:
        List of {project_id, title, status, effort_days}
    """
    blockers = list(graph.get_blocking_deps(project_id))

    result = []
    for blocker_id in blockers:
        if blocker_id not in projects:
            continue

        blocker = projects[blocker_id]
        effort = (blocker.estimate.effort_days or 0) if blocker.estimate else 0

        result.append({
            "project_id": blocker_id,
            "title": blocker.title,
            "status": blocker.status.value,
            "effort_days": effort,
        })

    return sorted(result, key=lambda x: x["effort_days"], reverse=True)
