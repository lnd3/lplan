"""Tests for dependency graph analysis."""

from datetime import date
import pytest
from planner.models import Project, Status, Priority
from planner.graph import DependencyGraph


class TestDependencyGraph:
    """Test DependencyGraph."""

    @staticmethod
    def _create_project(
        project_id: str, depends: list | None = None, enables: list | None = None
    ) -> Project:
        """Helper to create a project."""
        return Project(
            id=project_id,
            title=f"Project {project_id}",
            status=Status.PLANNING,
            priority=Priority.MEDIUM,
            priority_drivers=["strategic_edge"],
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
            depends=depends or [],
            enables=enables or [],
        )

    def test_simple_chain(self) -> None:
        """Test simple dependency chain: P001 <- P002 <- P003."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P002"]),
        }
        graph = DependencyGraph(projects)

        assert graph.has_cycles() is False
        assert graph.get_blocking_deps("P002") == ["P001"]
        assert graph.get_blocking_deps("P003") == ["P002"]

    def test_no_cycles(self) -> None:
        """Test DAG with no cycles."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P001"]),
        }
        graph = DependencyGraph(projects)

        assert graph.has_cycles() is False

    def test_cycle_detection(self) -> None:
        """Test cycle detection."""
        projects = {
            "P001": self._create_project("P001", depends=["P002"]),
            "P002": self._create_project("P002", depends=["P001"]),  # Circular!
        }
        graph = DependencyGraph(projects)

        assert graph.has_cycles() is True
        cycles = graph.find_cycles()
        assert len(cycles) > 0

    def test_get_blocking_deps(self) -> None:
        """Test getting direct dependencies."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P001", "P002"]),
        }
        graph = DependencyGraph(projects)

        assert graph.get_blocking_deps("P003") == ["P001", "P002"]

    def test_get_blocked_by(self) -> None:
        """Test getting projects that depend on this one."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P001"]),
        }
        graph = DependencyGraph(projects)

        blocked = sorted(graph.get_blocked_by("P001"))
        assert blocked == ["P002", "P003"]

    def test_transitive_deps(self) -> None:
        """Test transitive dependency tracking."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P002"]),
        }
        graph = DependencyGraph(projects)

        # P003 transitively depends on P001 and P002
        trans = graph.get_transitive_deps("P003")
        assert "P001" in trans
        assert "P002" in trans

    def test_transitive_dependents(self) -> None:
        """Test finding all projects that transitively depend on one."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P002"]),
        }
        graph = DependencyGraph(projects)

        # P001 is transitively depended on by P002 and P003
        trans = graph.get_transitive_dependents("P001")
        assert "P002" in trans
        assert "P003" in trans

    def test_find_roots(self) -> None:
        """Test finding root projects (no dependencies)."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003"),
        }
        graph = DependencyGraph(projects)

        roots = graph.find_roots()
        assert set(roots) == {"P001", "P003"}

    def test_find_leaves(self) -> None:
        """Test finding leaf projects (no dependents)."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P002"]),
        }
        graph = DependencyGraph(projects)

        leaves = graph.find_leaves()
        assert leaves == ["P003"]

    def test_impact_analysis(self) -> None:
        """Test impact analysis."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P001"]),
        }
        graph = DependencyGraph(projects)

        impact = graph.impact_analysis("P001")
        assert impact["directly_blocks"] == 2
        assert set(impact["blocks"]) == {"P002", "P003"}

    def test_cross_repo_refs(self) -> None:
        """Test handling of cross-repo references."""
        projects = {
            "P001": self._create_project("P001", depends=["ltools:L001"]),
            "P002": self._create_project("P002", depends=["P001"]),
        }
        graph = DependencyGraph(projects)

        assert "ltools:L001" in graph.cross_repo_refs
        # Should not error even though cross-repo ref doesn't exist locally
        assert graph.has_cycles() is False

    def test_topological_order(self) -> None:
        """Test topological ordering."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
            "P003": self._create_project("P003", depends=["P002"]),
        }
        graph = DependencyGraph(projects)

        order = graph.get_topological_order()
        assert order is not None
        # P001 should come before P002, and P002 before P003
        assert order.index("P001") < order.index("P002")
        assert order.index("P002") < order.index("P003")

    def test_topological_order_with_cycles(self) -> None:
        """Test that topological order returns None for cyclic graphs."""
        projects = {
            "P001": self._create_project("P001", depends=["P002"]),
            "P002": self._create_project("P002", depends=["P001"]),
        }
        graph = DependencyGraph(projects)

        order = graph.get_topological_order()
        assert order is None

    def test_graph_report(self) -> None:
        """Test full graph report generation."""
        projects = {
            "P001": self._create_project("P001"),
            "P002": self._create_project("P002", depends=["P001"]),
        }
        graph = DependencyGraph(projects)

        report = graph.get_report()
        assert report["total_projects"] == 2
        assert report["total_edges"] == 1
        assert report["has_cycles"] is False
        assert "root_projects" in report
        assert "leaf_projects" in report
