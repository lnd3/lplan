"""Tests for report.py module."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from planner.models import Project, Status, Priority
from planner.graph import DependencyGraph
from planner.stats import compute_stats
from planner.report import generate_html_report, write_report


@pytest.fixture
def sample_projects():
    """Create sample projects for reporting."""
    p1 = Project(
        id="P001",
        title="Core Engine",
        status=Status.DONE,
        priority=Priority.HIGH,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 1),
        updated=date(2026, 8, 21),
    )

    p2 = Project(
        id="P002",
        title="API Layer",
        status=Status.IN_PROGRESS,
        priority=Priority.HIGH,
        priority_drivers=["revenue_impact"],
        created=date(2026, 8, 15),
        updated=date(2026, 8, 21),
        depends=["P001"],
    )

    return {"P001": p1, "P002": p2}


def test_generate_html_report_structure(sample_projects):
    """Test that HTML report has required sections."""
    entities = {**sample_projects}
    graph = DependencyGraph(sample_projects)
    stats = compute_stats(entities)

    html = generate_html_report(entities, sample_projects, graph, stats)

    assert "<!doctype html>" in html
    assert "<title>Plan Report</title>" in html
    assert "Plan Report" in html
    assert "## Summary" not in html  # Should be HTML, not markdown
    assert "<h2>Summary</h2>" in html


def test_generate_html_report_contains_entities(sample_projects):
    """Test that HTML includes all entities."""
    entities = {**sample_projects}
    graph = DependencyGraph(sample_projects)
    stats = compute_stats(entities)

    html = generate_html_report(entities, sample_projects, graph, stats)

    assert "P001" in html
    assert "Core Engine" in html
    assert "P002" in html
    assert "API Layer" in html


def test_generate_html_report_contains_stats(sample_projects):
    """Test that HTML includes statistics."""
    entities = {**sample_projects}
    graph = DependencyGraph(sample_projects)
    stats = compute_stats(entities)

    html = generate_html_report(entities, sample_projects, graph, stats)

    assert "2" in html  # 2 projects
    assert "50" in html  # 50% done (1 out of 2)


def test_generate_html_report_svg_graph(sample_projects):
    """Test that HTML includes SVG dependency graph."""
    entities = {**sample_projects}
    graph = DependencyGraph(sample_projects)
    stats = compute_stats(entities)

    html = generate_html_report(entities, sample_projects, graph, stats)

    assert "<svg" in html
    assert "</svg>" in html


def test_write_report_creates_file(sample_projects):
    """Test that write_report creates output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        output_path = plan_dir / "report.html"

        entities = {**sample_projects}
        result_path = write_report(plan_dir, entities, output_path)

        assert result_path.exists()
        assert result_path.name == "report.html"
        content = result_path.read_text()
        assert "<!doctype html>" in content
