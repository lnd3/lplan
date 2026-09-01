"""Tests for data models."""

from datetime import date
import pytest
from planner.models import Project, Design, Action, Status, Priority, PlanEntity


class TestStatus:
    """Test Status enum."""

    def test_valid_statuses(self) -> None:
        """Test all valid status values."""
        assert Status.IDEA.value == "IDEA"
        assert Status.PLANNING.value == "PLANNING"
        assert Status.IN_PROGRESS.value == "IN_PROGRESS"
        assert Status.BLOCKED.value == "BLOCKED"
        assert Status.DONE.value == "DONE"
        assert Status.DEFERRED.value == "DEFERRED"
        assert Status.CANCELLED.value == "CANCELLED"


class TestProject:
    """Test Project model."""

    def test_create_valid_project(self) -> None:
        """Test creating a valid project."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=["strategic_edge"],
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert project.id == "P001"
        assert project.priority == Priority.HIGH

    def test_project_depends(self) -> None:
        """Test project dependencies."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=["strategic_edge"],
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
            depends=["P002", "tradeflow:P003"],
        )
        assert project.depends == ["P002", "tradeflow:P003"]

    def test_project_enables(self) -> None:
        """Test project enables (unblocks)."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=["strategic_edge"],
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
            enables=["P002"],
        )
        assert project.enables == ["P002"]

    def test_invalid_id_format(self) -> None:
        """Test that invalid ID format raises error."""
        with pytest.raises(ValueError, match="Invalid ID format"):
            Project(
                id="999",  # Invalid: doesn't start with letter
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            )

    def test_updated_before_created_fails(self) -> None:
        """Test that updated < created raises error."""
        with pytest.raises(ValueError, match="updated date must be"):
            Project(
                id="P001",
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 19),  # Before created
            )

    def test_priority_drivers_omitted_defaults_empty(self) -> None:
        """Omitting priority_drivers must not raise at parse time; it defaults to []."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert project.priority_drivers == []

    def test_empty_priority_drivers_allowed_at_model_level(self) -> None:
        """Empty priority_drivers no longer raises at model level (enforced by SchemaValidator instead)."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=[],  # Empty
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert project.priority_drivers == []


class TestDesign:
    """Test Design model."""

    def test_create_valid_design(self) -> None:
        """Test creating a valid design."""
        design = Design(
            id="D001",
            title="Test Design",
            status=Status.PLANNING,
            project="P001",
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert design.id == "D001"
        assert design.project == "P001"

    def test_design_cannot_be_blocked(self) -> None:
        """Test that designs cannot have BLOCKED status."""
        with pytest.raises(ValueError, match="cannot have BLOCKED"):
            Design(
                id="D001",
                title="Test",
                status=Status.BLOCKED,
                project="P001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            )


class TestAction:
    """Test Action model."""

    def test_create_valid_action(self) -> None:
        """Test creating a valid action."""
        action = Action(
            id="A001",
            title="Test Action",
            status=Status.IN_PROGRESS,
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert action.id == "A001"

    def test_action_with_design(self) -> None:
        """Test action with parent design."""
        action = Action(
            id="A001",
            title="Test",
            status=Status.IN_PROGRESS,
            design="D001",
            project="P001",
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert action.design == "D001"
        assert action.project == "P001"

    def test_action_with_priority(self) -> None:
        """Test action with priority (if independent)."""
        action = Action(
            id="A001",
            title="Test",
            status=Status.IN_PROGRESS,
            priority=Priority.HIGH,
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        assert action.priority == Priority.HIGH
