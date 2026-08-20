"""Tests for writer.py module."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from planner.writer import update_entity_frontmatter, append_log_entry


@pytest.fixture
def sample_project_file():
    """Create a sample project file for testing."""
    content = """---
id: P001
title: Test Project
status: PLANNING
priority: HIGH
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-20
---

## Goal
This is the goal.

## Scope
This is the scope.
"""
    return content


def test_update_entity_frontmatter_status(sample_project_file):
    """Test updating status field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "P001.md"
        filepath.write_text(sample_project_file)

        update_entity_frontmatter(filepath, {"status": "IN_PROGRESS"})

        content = filepath.read_text()
        assert "status: IN_PROGRESS" in content
        assert "## Goal" in content  # Body preserved
        assert "This is the goal" in content


def test_update_entity_frontmatter_multiple(sample_project_file):
    """Test updating multiple fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "P001.md"
        filepath.write_text(sample_project_file)

        update_entity_frontmatter(
            filepath,
            {"status": "DONE", "updated": "2026-08-25"}
        )

        content = filepath.read_text()
        assert "status: DONE" in content
        assert "updated: '2026-08-25'" in content or "updated: 2026-08-25" in content


def test_update_entity_frontmatter_invalid_file():
    """Test error handling for missing frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "invalid.md"
        filepath.write_text("No frontmatter here")

        with pytest.raises(ValueError, match="does not start with frontmatter"):
            update_entity_frontmatter(filepath, {"status": "DONE"})


def test_append_log_entry_creates_section(sample_project_file):
    """Test creating Log section if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "P001.md"
        filepath.write_text(sample_project_file)

        append_log_entry(filepath, "Initial log entry", date(2026, 8, 21))

        content = filepath.read_text()
        assert "## Log" in content
        assert "2026-08-21 — Initial log entry" in content


def test_append_log_entry_to_existing_section(sample_project_file):
    """Test appending to existing Log section."""
    content = sample_project_file + "\n## Log\n\n2026-08-20 — First entry\n"

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "P001.md"
        filepath.write_text(content)

        append_log_entry(filepath, "Second entry", date(2026, 8, 21))

        updated = filepath.read_text()
        assert "2026-08-21 — Second entry" in updated
        assert "2026-08-20 — First entry" in updated


def test_append_log_entry_preserves_body(sample_project_file):
    """Test that log entries don't corrupt other sections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "P001.md"
        filepath.write_text(sample_project_file)

        append_log_entry(filepath, "Test log", date(2026, 8, 21))

        content = filepath.read_text()
        assert "## Goal" in content
        assert "This is the goal" in content
        assert "## Scope" in content
        assert "This is the scope" in content
