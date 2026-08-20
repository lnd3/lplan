"""Tests for plan file parser."""

from pathlib import Path
import tempfile
import pytest
from planner.parser import PlanParser
from planner.models import Status, Priority


class TestPlanParser:
    """Test PlanParser."""

    def test_parse_project_file(self) -> None:
        """Test parsing a project file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            project_dir = tmpdir_path / "projects"
            project_dir.mkdir()

            # Write test file
            project_file = project_dir / "P001-test.md"
            project_file.write_text("""---
id: P001
title: Test Project
status: PLANNING
priority: HIGH
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-20
depends:
  - P002
---

## Goal
Test goal description

## Scope
- Item 1
- Item 2

## Tasks
- [x] Task 1
- [ ] Task 2
""")

            # Parse it
            plan_file = PlanParser.parse_file(project_file)

            assert plan_file.entity.id == "P001"
            assert plan_file.entity.title == "Test Project"
            assert plan_file.entity.status == Status.PLANNING
            assert plan_file.entity.priority == Priority.HIGH
            assert plan_file.entity.depends == ["P002"]
            assert "Test goal" in plan_file.goal
            assert len(plan_file.tasks) == 2

    def test_parse_design_file(self) -> None:
        """Test parsing a design file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            design_dir = tmpdir_path / "designs"
            design_dir.mkdir()

            design_file = design_dir / "D001-test.md"
            design_file.write_text("""---
id: D001
title: Test Design
status: IN_PROGRESS
project: P001
created: 2026-08-20
updated: 2026-08-20
---

## Goal
Design goal
""")

            plan_file = PlanParser.parse_file(design_file)

            assert plan_file.entity.id == "D001"
            assert plan_file.entity.status == Status.IN_PROGRESS

    def test_parse_action_file(self) -> None:
        """Test parsing an action file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            action_dir = tmpdir_path / "actions"
            action_dir.mkdir()

            action_file = action_dir / "A001-test.md"
            action_file.write_text("""---
id: A001
title: Test Action
status: IN_PROGRESS
design: D001
project: P001
created: 2026-08-20
updated: 2026-08-20
---

## Goal
Action goal
""")

            plan_file = PlanParser.parse_file(action_file)

            assert plan_file.entity.id == "A001"
            assert plan_file.entity.status == Status.IN_PROGRESS

    def test_parse_directory(self) -> None:
        """Test parsing an entire plan directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create structure
            (tmpdir_path / "projects").mkdir()
            (tmpdir_path / "designs").mkdir()
            (tmpdir_path / "actions").mkdir()

            # Write test files
            (tmpdir_path / "projects" / "P001-test.md").write_text("""---
id: P001
title: Test
status: PLANNING
priority: HIGH
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-20
---

## Goal
Test
""")

            (tmpdir_path / "designs" / "D001-test.md").write_text("""---
id: D001
title: Test
status: PLANNING
project: P001
created: 2026-08-20
updated: 2026-08-20
---

## Goal
Test
""")

            # Parse
            results = PlanParser.parse_directory(tmpdir_path)

            assert len(results) == 2
            # Find P001
            p001_found = False
            for plan_file in results.values():
                if not isinstance(plan_file, dict) or "error" not in plan_file:
                    if plan_file.entity.id == "P001":
                        p001_found = True
                        break
            assert p001_found

    def test_extract_sections(self) -> None:
        """Test markdown section extraction."""
        body = """
## Goal
This is the goal.

## Scope
This is the scope.

## Tasks
- [x] Done task
- [ ] Pending task

## Log
2026-08-20 — Entry 1
2026-08-19 — Entry 2
"""

        sections = PlanParser._extract_sections(body)

        assert "goal" in sections
        assert "scope" in sections
        assert "tasks" in sections
        assert len(sections["tasks"]) == 2
        assert "log" in sections
        assert len(sections["log"]) == 2

    def test_malformed_frontmatter(self) -> None:
        """Test error handling for malformed frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "projects").mkdir()

            project_file = tmpdir_path / "projects" / "P001-bad.md"
            project_file.write_text("""No frontmatter here""")

            with pytest.raises(ValueError):
                PlanParser.parse_file(project_file)

    def test_invalid_yaml(self) -> None:
        """Test error handling for invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "projects").mkdir()

            project_file = tmpdir_path / "projects" / "P001-bad.md"
            project_file.write_text("""---
id: P001
title: Test
  invalid: indentation here
---

Content
""")

            with pytest.raises(ValueError, match="Invalid YAML"):
                PlanParser.parse_file(project_file)

    def test_date_parsing(self) -> None:
        """Test that date strings are parsed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "projects").mkdir()

            project_file = tmpdir_path / "projects" / "P001-test.md"
            project_file.write_text("""---
id: P001
title: Test
status: PLANNING
priority: HIGH
priority_drivers:
  - strategic_edge
created: 2026-08-20
updated: 2026-08-21
---

## Goal
Test
""")

            plan_file = PlanParser.parse_file(project_file)
            assert plan_file.entity.created.year == 2026
            assert plan_file.entity.created.month == 8
            assert plan_file.entity.created.day == 20
