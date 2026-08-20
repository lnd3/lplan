"""Tests for stats.py module."""

from datetime import date

import pytest

from planner.models import Project, Design, Action, Status, Priority, Estimate
from planner.graph import DependencyGraph
from planner.stats import (
    compute_stats,
    compute_timeline,
    compute_estimates,
    compute_velocity,
)


@pytest.fixture
def sample_projects():
    """Create sample projects for testing."""
    p1 = Project(
        id="P001",
        title="Core",
        status=Status.DONE,
        priority=Priority.HIGH,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 1),
        updated=date(2026, 8, 21),
        estimate=Estimate(
            effort_days=8.0,
            confidence="high",
            started=date(2026, 8, 1),
            completed=date(2026, 8, 9),
        ),
    )

    p2 = Project(
        id="P002",
        title="API",
        status=Status.IN_PROGRESS,
        priority=Priority.HIGH,
        priority_drivers=["revenue_impact"],
        created=date(2026, 8, 15),
        updated=date(2026, 8, 21),
        depends=["P001"],
    )

    p3 = Project(
        id="P003",
        title="UI",
        status=Status.PLANNING,
        priority=Priority.MEDIUM,
        priority_drivers=["user_experience"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
        depends=["P002"],
    )

    return {"P001": p1, "P002": p2, "P003": p3}


def test_compute_stats_counts(sample_projects):
    """Test entity counting."""
    entities = {**sample_projects}
    stats = compute_stats(entities)

    assert stats["projects_total"] == 3
    assert stats["by_status"]["DONE"] == 1
    assert stats["by_status"]["IN_PROGRESS"] == 1
    assert stats["by_status"]["PLANNING"] == 1


def test_compute_stats_percent_done(sample_projects):
    """Test percent done calculation."""
    entities = {**sample_projects}
    stats = compute_stats(entities)

    # 1 out of 3 projects is DONE
    assert pytest.approx(stats["percent_done"], 0.1) == 33.3


def test_compute_timeline_phases(sample_projects):
    """Test timeline phase computation."""
    graph = DependencyGraph(sample_projects)
    timeline = compute_timeline(sample_projects, graph)

    # Should have 3 phases: P001 alone, then P002, then P003
    assert len(timeline) == 3
    assert timeline[0] == (0, ["P001"])
    assert timeline[1] == (1, ["P002"])
    assert timeline[2] == (2, ["P003"])


def test_compute_estimates_rollup(sample_projects):
    """Test estimate rollup."""
    est_stats = compute_estimates(sample_projects)

    assert est_stats["total_effort_days"] == 8.0
    assert est_stats["projects_with_estimates"] == 1
    assert est_stats["projects_without_estimates"] == 2


def test_compute_estimates_by_status(sample_projects):
    """Test estimates broken down by status."""
    est_stats = compute_estimates(sample_projects)

    assert "DONE" in est_stats["by_status"]
    assert est_stats["by_status"]["DONE"] == (8.0, 1)


def test_compute_velocity_completed(sample_projects):
    """Test velocity for completed projects."""
    vel_stats = compute_velocity(sample_projects)

    assert vel_stats["completed_projects"] == 1
    assert len(vel_stats["projects"]) == 1
    assert vel_stats["projects"][0]["id"] == "P001"
    assert vel_stats["projects"][0]["effort_days"] == 8.0
    assert vel_stats["projects"][0]["actual_days"] == 8


def test_compute_velocity_variance():
    """Test variance calculation in velocity."""
    p_on_time = Project(
        id="P001",
        title="On Time",
        status=Status.DONE,
        priority=Priority.HIGH,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 1),
        updated=date(2026, 8, 21),
        estimate=Estimate(
            effort_days=10.0,
            confidence="high",
            started=date(2026, 8, 1),
            completed=date(2026, 8, 11),
        ),
    )

    vel_stats = compute_velocity({"P001": p_on_time})

    # 10 actual vs 10 estimated = 0% variance
    assert vel_stats["projects"][0]["variance_percent"] == 0.0


def test_compute_velocity_no_complete_estimates(sample_projects):
    """Test when no projects have complete estimate data."""
    # sample_projects[P001] has estimates, but others don't
    vel_stats = compute_velocity(
        {"P002": sample_projects["P002"], "P003": sample_projects["P003"]}
    )

    assert vel_stats["completed_projects"] == 0
    assert vel_stats["incomplete_estimates"] == 0
