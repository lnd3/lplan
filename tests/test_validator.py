"""Tests for schema validator."""

from datetime import date
import pytest
from planner.models import Project, Design, Action, Status, Priority
from planner.validator import SchemaValidator


class TestSchemaValidator:
    """Test SchemaValidator."""

    def test_validate_valid_project(self) -> None:
        """Test validating a valid project."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=["strategic_edge"],
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        validator = SchemaValidator()
        assert validator.validate_entity(project) is True
        assert len(validator.errors) == 0

    def test_validate_project_empty_drivers(self) -> None:
        """Test that empty priority_drivers fails."""
        # This would fail during model creation, so we test via direct instantiation
        with pytest.raises(ValueError):
            Project(
                id="P001",
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=[],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            )

    def test_validate_valid_design(self) -> None:
        """Test validating a valid design."""
        design = Design(
            id="D001",
            title="Test",
            status=Status.PLANNING,
            project="P001",
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        validator = SchemaValidator()
        assert validator.validate_entity(design) is True

    def test_validate_design_blocked_fails(self) -> None:
        """Test that designs cannot be BLOCKED."""
        with pytest.raises(ValueError, match="cannot have BLOCKED"):
            Design(
                id="D001",
                title="Test",
                status=Status.BLOCKED,
                project="P001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            )

    def test_validate_valid_action(self) -> None:
        """Test validating a valid action."""
        action = Action(
            id="A001",
            title="Test",
            status=Status.IN_PROGRESS,
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        validator = SchemaValidator()
        assert validator.validate_entity(action) is True

    def test_validate_relationships_valid(self) -> None:
        """Test relationship validation with valid references."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
                depends=["P002"],
            ),
            "P002": Project(
                id="P002",
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
        }

        validator = SchemaValidator()
        assert validator.validate_relationships(entities) is True
        assert len(validator.errors) == 0

    def test_validate_relationships_missing_dep(self) -> None:
        """Test that missing dependencies are caught."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
                depends=["P002"],  # P002 doesn't exist
            ),
        }

        validator = SchemaValidator()
        assert validator.validate_relationships(entities) is False
        assert len(validator.errors) > 0

    def test_validate_relationships_missing_project(self) -> None:
        """Test that designs with missing projects generate warnings."""
        entities = {
            "D001": Design(
                id="D001",
                title="Test",
                status=Status.PLANNING,
                project="P001",  # P001 doesn't exist
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
        }

        validator = SchemaValidator()
        validator.validate_relationships(entities)
        assert len(validator.warnings) > 0

    def test_validate_relationships_cross_repo(self) -> None:
        """Test that cross-repo references are allowed."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.PLANNING,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
                depends=["ltools:L001"],  # Cross-repo ref
            ),
        }

        validator = SchemaValidator()
        assert validator.validate_relationships(entities) is True

    def test_get_report(self) -> None:
        """Test validation report generation."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=["strategic_edge"],
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )

        validator = SchemaValidator()
        validator.validate_entity(project)
        report = validator.get_report()

        assert "errors" in report
        assert "warnings" in report
        assert "error_count" in report
        assert "warning_count" in report
        assert "valid" in report
        assert report["valid"] is True
