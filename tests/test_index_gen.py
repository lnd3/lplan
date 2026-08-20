"""Tests for index_gen.py module."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from planner.models import Project, Design, Action, Status, Priority
from planner.index_gen import generate_index, write_index, append_changelog


@pytest.fixture
def sample_entities():
    """Create sample entities for testing."""
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
        priority=Priority.MEDIUM,
        priority_drivers=["revenue_impact"],
        created=date(2026, 8, 15),
        updated=date(2026, 8, 21),
    )

    d1 = Design(
        id="D001",
        title="API Design",
        status=Status.PLANNING,
        project="P002",
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
    )

    a1 = Action(
        id="A001",
        title="Fix bugs",
        status=Status.IN_PROGRESS,
        created=date(2026, 8, 20),
        updated=date(2026, 8, 21),
    )

    return {"P001": p1, "P002": p2, "D001": d1, "A001": a1}


def test_generate_index_structure(sample_entities):
    """Test that INDEX.md has correct structure."""
    index_md = generate_index(sample_entities, "Test Repo")

    assert "# Test Repo Plan Index" in index_md
    assert "Last updated:" in index_md
    assert "## Projects" in index_md
    assert "## Designs" in index_md
    assert "## Actions" in index_md


def test_generate_index_contains_entities(sample_entities):
    """Test that all entities appear in index."""
    index_md = generate_index(sample_entities, "Test Repo")

    assert "[P001]" in index_md
    assert "Core Engine" in index_md
    assert "[D001]" in index_md
    assert "[A001]" in index_md


def test_generate_index_status_priority(sample_entities):
    """Test that status and priority are shown."""
    index_md = generate_index(sample_entities, "Test Repo")

    assert "DONE" in index_md
    assert "IN_PROGRESS" in index_md
    assert "HIGH" in index_md
    assert "MEDIUM" in index_md


def test_write_index_creates_file(sample_entities):
    """Test that write_index creates INDEX.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)
        result_path = write_index(plan_dir, sample_entities, "Test")

        assert result_path.exists()
        assert result_path.name == "INDEX.md"
        content = result_path.read_text()
        assert "# Test Plan Index" in content


def test_append_changelog_creates_file():
    """Test creating CHANGELOG.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)

        append_changelog(
            plan_dir,
            "P001",
            "PLANNING",
            "IN_PROGRESS",
            "Started work",
            date(2026, 8, 21)
        )

        changelog_path = plan_dir / "CHANGELOG.md"
        assert changelog_path.exists()
        content = changelog_path.read_text()
        assert "P001" in content
        assert "PLANNING → IN_PROGRESS" in content


def test_append_changelog_appends_to_existing():
    """Test appending to existing CHANGELOG.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)

        # Create first entry
        append_changelog(
            plan_dir, "P001", "PLANNING", "IN_PROGRESS", "First",
            date(2026, 8, 20)
        )

        # Create second entry
        append_changelog(
            plan_dir, "P002", "IDEA", "PLANNING", "Second",
            date(2026, 8, 21)
        )

        content = (plan_dir / "CHANGELOG.md").read_text()
        assert "P001" in content
        assert "P002" in content
        # Check for both entries (arrow appears in template + entries)
        assert "PLANNING → IN_PROGRESS" in content
        assert "IDEA → PLANNING" in content
