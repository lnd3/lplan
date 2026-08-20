"""Tests for init.py module."""

import tempfile
from pathlib import Path

import pytest

from planner.init import init_plan, _slugify
from planner.parser import PlanParser


def test_slugify():
    """Test slug generation."""
    assert _slugify("Hello World") == "hello-world"
    assert _slugify("Multi  Space") == "multi-space"
    assert _slugify("With-Dashes") == "with-dashes"
    assert _slugify("Special!@#$%Characters") == "specialcharacters"


def test_init_plan_creates_directories():
    """Test that init_plan creates required directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / "test-plan"

        init_plan(plan_dir, "Test Repo")

        assert (plan_dir / "projects").exists()
        assert (plan_dir / "designs").exists()
        assert (plan_dir / "actions").exists()


def test_init_plan_creates_index_and_changelog():
    """Test that INDEX.md and CHANGELOG.md are created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)

        init_plan(plan_dir, "Test Repo")

        assert (plan_dir / "INDEX.md").exists()
        assert (plan_dir / "CHANGELOG.md").exists()

        index_content = (plan_dir / "INDEX.md").read_text()
        assert "Test Repo" in index_content


def test_init_plan_creates_first_project():
    """Test that first project is created if requested."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)

        init_plan(plan_dir, "Test Repo", "Initial Project")

        # Find P001 file
        p001_files = list(plan_dir.glob("projects/P001-*.md"))
        assert len(p001_files) == 1

        # Verify it's valid
        parsed = PlanParser.parse_file(p001_files[0])
        assert parsed.entity.id == "P001"
        assert parsed.entity.title == "Initial Project"


def test_init_plan_first_project_has_today_date():
    """Test that first project has today's date."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)

        init_plan(plan_dir, "Test Repo", "Project")

        p001_files = list(plan_dir.glob("projects/P001-*.md"))
        parsed = PlanParser.parse_file(p001_files[0])

        # Created and updated should be set
        assert parsed.entity.created is not None
        assert parsed.entity.updated is not None


def test_init_plan_idempotent():
    """Test that init_plan is idempotent (can run multiple times)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir)

        init_plan(plan_dir, "Test Repo", "Project")
        init_plan(plan_dir, "Test Repo", "Another Project")

        # Should not create duplicate P001 files
        p001_files = list(plan_dir.glob("projects/P001-*.md"))
        assert len(p001_files) == 1
