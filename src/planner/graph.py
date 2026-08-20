"""Dependency graph analysis for projects."""

from typing import Dict, List, Set, Tuple, Optional
import networkx as nx
from .models import Project, PlanEntity


class DependencyGraph:
    """Dependency graph resolver with cycle detection and analysis."""

    def __init__(self, projects: Dict[str, Project]):
        """Initialize graph from projects.

        Args:
            projects: Dict mapping project ID to Project entity
        """
        self.projects = projects
        self.graph = nx.DiGraph()
        self.cross_repo_refs: Set[str] = set()
        self._build_graph()

    def _build_graph(self) -> None:
        """Build dependency graph from projects."""
        # Add all nodes
        for project_id in self.projects:
            self.graph.add_node(project_id)

        # Add edges (depends relationships)
        for project_id, project in self.projects.items():
            for dep in project.depends:
                if ":" in dep:
                    # Cross-repo ref: repo:ID
                    self.cross_repo_refs.add(dep)
                    # Still add edge for analysis, mark as external
                    self.graph.add_node(dep)
                    self.graph.add_edge(project_id, dep, cross_repo=True)
                else:
                    # Local ref
                    if dep in self.projects:
                        self.graph.add_edge(project_id, dep, cross_repo=False)

    def has_cycles(self) -> bool:
        """Check if graph has cycles."""
        return not nx.is_directed_acyclic_graph(self.graph)

    def find_cycles(self) -> List[List[str]]:
        """Find all cycles in the graph."""
        try:
            return list(nx.algorithms.simple_cycles(self.graph))
        except:
            return []

    def get_blocking_deps(self, project_id: str) -> List[str]:
        """Get projects that block the given project (its dependencies).

        Args:
            project_id: The project to check

        Returns:
            List of project IDs this project depends on
        """
        if project_id not in self.projects:
            return []

        return list(self.graph.successors(project_id))

    def get_blocked_by(self, project_id: str) -> List[str]:
        """Get projects blocked by this one (projects that depend on it).

        Args:
            project_id: The project to check

        Returns:
            List of project IDs that depend on this one
        """
        if project_id not in self.projects:
            return []

        return list(self.graph.predecessors(project_id))

    def get_transitive_deps(self, project_id: str) -> Set[str]:
        """Get all transitive dependencies of a project.

        Args:
            project_id: The project to check

        Returns:
            Set of all projects (directly or indirectly) this depends on
        """
        if project_id not in self.graph:
            return set()

        # Use networkx to find all descendants
        descendants = set()
        for successor in nx.descendants(self.graph, project_id):
            if successor in self.projects:  # Only include local projects
                descendants.add(successor)

        return descendants

    def get_transitive_dependents(self, project_id: str) -> Set[str]:
        """Get all projects that transitively depend on this one.

        Args:
            project_id: The project to check

        Returns:
            Set of all projects (directly or indirectly) that depend on this
        """
        if project_id not in self.graph:
            return set()

        # Use networkx to find all ancestors
        ancestors = set()
        for ancestor in nx.ancestors(self.graph, project_id):
            if ancestor in self.projects:  # Only include local projects
                ancestors.add(ancestor)

        return ancestors

    def get_critical_path(self) -> List[str]:
        """Find longest path in DAG (critical path).

        Returns:
            List of project IDs representing critical path, or empty if cycle detected
        """
        if self.has_cycles():
            return []

        # Find longest path in DAG
        try:
            longest_path = max(
                nx.algorithms.dag.all_simple_paths(
                    self.graph,
                    source=node,
                    target=node,
                )
                for node in self.graph.nodes()
            )
            return longest_path
        except (ValueError, nx.NetworkXError):
            # No paths found or other error
            return []

    def get_topological_order(self) -> Optional[List[str]]:
        """Get topological sort of projects (execution order).

        Returns:
            List of project IDs in order (dependencies first), or None if cycles exist
        """
        if self.has_cycles():
            return None

        try:
            # topological_sort gives nodes in topological order based on edge direction
            # Since edges point from dependent to dependency (P002 -> P001 means P002 depends on P001),
            # we need to reverse to get execution order (dependencies before dependents)
            local_projects_only = [
                p for p in reversed(list(nx.topological_sort(self.graph))) if p in self.projects
            ]
            return local_projects_only
        except nx.NetworkXError:
            return None

    def find_roots(self) -> List[str]:
        """Find projects with no dependencies (can start immediately).

        Returns:
            List of project IDs with out-degree 0 (no dependencies)
        """
        roots = [p for p in self.projects if self.graph.out_degree(p) == 0]
        return sorted(roots)

    def find_leaves(self) -> List[str]:
        """Find projects that have no dependents (end goals).

        Returns:
            List of project IDs with in-degree 0 (nothing depends on them)
        """
        leaves = [p for p in self.projects if self.graph.in_degree(p) == 0]
        return sorted(leaves)

    def impact_analysis(self, project_id: str) -> Dict[str, object]:
        """Analyze impact of completing a project.

        Args:
            project_id: The project to analyze

        Returns:
            Dict with:
            - project: the project ID
            - blocks: list of projects blocked by it
            - transitively_unblocks: list of projects indirectly unblocked
            - critical_for: whether on critical path
        """
        blocked_by_this = self.get_blocked_by(project_id)
        transitive = self.get_transitive_dependents(project_id)

        return {
            "project": project_id,
            "directly_blocks": len(blocked_by_this),
            "blocks": blocked_by_this,
            "transitively_unblocks": len(transitive),
            "transitive_dependents": list(transitive),
        }

    def dependency_matrix(self) -> Dict[str, Dict[str, int]]:
        """Generate dependency matrix (DSM-like format).

        Returns:
            Dict mapping project IDs to dicts of dependent project IDs and their depth
        """
        matrix: Dict[str, Dict[str, int]] = {}

        for project_id in self.projects:
            matrix[project_id] = {}
            deps = self.graph.successors(project_id)
            for dep in deps:
                if dep in self.projects:
                    matrix[project_id][dep] = 1

        return matrix

    def get_report(self) -> Dict[str, object]:
        """Generate full dependency analysis report."""
        cycles = self.find_cycles()
        roots = self.find_roots()
        leaves = self.find_leaves()
        topo_order = self.get_topological_order()

        return {
            "total_projects": len(self.projects),
            "total_edges": self.graph.number_of_edges(),
            "has_cycles": self.has_cycles(),
            "cycles": cycles,
            "root_projects": roots,
            "leaf_projects": leaves,
            "topological_order": topo_order,
            "cross_repo_refs": list(self.cross_repo_refs),
        }
