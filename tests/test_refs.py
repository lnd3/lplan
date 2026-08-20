"""Tests for refs.py module."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from planner.models import Project, Design, Action, Status, Priority
from planner.refs import check_references


@pytest.fixture
def sample_entities():
    """Create entities for reference testing."""
    p1 = Project(
        id="P001",
        title="Core",
        status=Status.PLANNING,
        priority=Priority.HIGH,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
    )

    p2 = Project(
        id="P002",
        title="API",
        status=Status.PLANNING,
        priority=Priority.HIGH,
        priority_drivers=["revenue_impact"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
        depends=["P001"],
    )

    # Orphaned design (parent doesn't exist)
    d_orphan = Design(
        id="D001",
        title="Orphan Design",
        status=Status.PLANNING,
        project="P999",
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
    )

    # Valid design
    d_valid = Design(
        id="D002",
        title="Valid Design",
        status=Status.PLANNING,
        project="P001",
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
    )

    return {
        "P001": p1,
        "P002": p2,
        "D001": d_orphan,
        "D002": d_valid,
    }


def test_check_references_counts(sample_entities):
    """Test that references are counted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        report = check_references(sample_entities, plan_dir)

        assert report["local_refs_checked"] > 0


def test_check_references_orphaned_design(sample_entities):
    """Test detection of orphaned designs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        report = check_references(sample_entities, plan_dir)

        assert "D001" in report["orphaned_designs"]
        assert "D002" not in report["orphaned_designs"]


def test_check_references_valid_deps():
    """Test that valid dependencies don't raise errors."""
    p1 = Project(
        id="P001",
        title="Core",
        status=Status.PLANNING,
        priority=Priority.HIGH,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
    )

    p2 = Project(
        id="P002",
        title="API",
        status=Status.PLANNING,
        priority=Priority.HIGH,
        priority_drivers=["revenue_impact"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
        depends=["P001"],  # Valid reference
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        report = check_references({"P001": p1, "P002": p2}, plan_dir)

        assert len(report["unresolvable_refs"]) == 0


def test_check_references_unresolvable_refs():
    """Test detection of unresolvable references."""
    p1 = Project(
        id="P001",
        title="Core",
        status=Status.PLANNING,
        priority=Priority.HIGH,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
        depends=["P999"],  # Invalid reference
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        report = check_references({"P001": p1}, plan_dir)

        assert len(report["unresolvable_refs"]) > 0
        assert report["unresolvable_refs"][0]["ref"] == "P999"


def test_check_references_unused_projects():
    """Test detection of unused projects."""
    p_unused = Project(
        id="P001",
        title="Unused",
        status=Status.PLANNING,
        priority=Priority.LOW,
        priority_drivers=["strategic_edge"],
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
        depends=[],
        enables=[],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        report = check_references({"P001": p_unused}, plan_dir)

        # P001 has no dependencies and nothing depends on it
        assert "P001" in report["unused_projects"]
