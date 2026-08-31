"""Tests for schema validator."""

from datetime import date
import pytest
from planner.models import Project, Design, Action, PlanFile, Status, Priority
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

    def test_validate_relationships_done_project_with_open_child_warns(self) -> None:
        """A027: DONE project with a non-terminal child Action warns."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.DONE,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
            "A001": Action(
                id="A001",
                title="Test action",
                status=Status.IN_PROGRESS,
                project="P001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
        }

        validator = SchemaValidator()
        validator.validate_relationships(entities)
        assert any(
            w.entity_id == "P001" and "A001" in w.message for w in validator.warnings
        )

    def test_validate_relationships_done_design_with_blocked_child_warns(self) -> None:
        """A027: DONE design with a BLOCKED child Action warns."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.IN_PROGRESS,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
            "D001": Design(
                id="D001",
                title="Test design",
                status=Status.DONE,
                project="P001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
            "A001": Action(
                id="A001",
                title="Test action",
                status=Status.BLOCKED,
                design="D001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
        }

        validator = SchemaValidator()
        validator.validate_relationships(entities)
        assert any(
            w.entity_id == "D001" and "A001" in w.message for w in validator.warnings
        )

    def test_validate_relationships_done_parent_terminal_children_no_warning(self) -> None:
        """A027: DONE project whose children are all DONE/DEFERRED/CANCELLED is silent."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.DONE,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
            "A001": Action(
                id="A001",
                title="Test action",
                status=Status.DONE,
                project="P001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
            "A002": Action(
                id="A002",
                title="Abandoned action",
                status=Status.CANCELLED,
                project="P001",
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
        }

        validator = SchemaValidator()
        validator.validate_relationships(entities)
        assert not any(w.entity_id == "P001" for w in validator.warnings)

    def test_validate_relationships_done_parent_no_children_no_warning(self) -> None:
        """A027: DONE project with no children at all doesn't crash or warn."""
        entities = {
            "P001": Project(
                id="P001",
                title="Test",
                status=Status.DONE,
                priority=Priority.HIGH,
                priority_drivers=["strategic_edge"],
                created=date(2026, 8, 20),
                updated=date(2026, 8, 20),
            ),
        }

        validator = SchemaValidator()
        validator.validate_relationships(entities)
        assert not any(w.entity_id == "P001" for w in validator.warnings)

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

    def test_validate_phase_anchors_no_phases_section_silent(self) -> None:
        """D008: a project with no ## Phases section isn't opted in — no warnings."""
        raw = "## Tasks\n\n### Phase 1: Something\n- [ ] a task\n"
        validator = SchemaValidator()
        assert validator.validate_phase_anchors({"P001": raw}, {}) is True
        assert len(validator.warnings) == 0

    def test_validate_phase_anchors_anchored_phase_silent(self) -> None:
        """D008: a phase header referencing a real Design is silent."""
        raw = "## Phases\n\n### Phase 1 — Strategy [D001 DONE]\n- [x] thing\n"
        design = Design(
            id="D001", title="t", status=Status.DONE, project="P001",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        validator = SchemaValidator()
        assert validator.validate_phase_anchors({"P001": raw}, {"D001": design}) is True
        assert len(validator.warnings) == 0

    def test_validate_phase_anchors_no_refs_warns(self) -> None:
        """D008: a phase header with no bracketed refs at all warns."""
        raw = "## Phases\n\n### Phase 2 — No anchor\n- [ ] thing\n"
        validator = SchemaValidator()
        assert validator.validate_phase_anchors({"P001": raw}, {}) is False
        assert any(w.entity_id == "P001" and "no Design anchor" in w.message for w in validator.warnings)

    def test_validate_phase_anchors_ref_not_a_design_warns(self) -> None:
        """D008: bracketed refs that don't resolve to any Design still warn."""
        raw = "## Phases\n\n### Phase 3 — Bad ref [A999, P001]\n- [ ] thing\n"
        project = Project(
            id="P001", title="t", status=Status.PLANNING, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        validator = SchemaValidator()
        # A999 doesn't exist at all; P001 exists but is a Project, not a Design.
        assert validator.validate_phase_anchors({"P001": raw}, {"P001": project}) is False
        assert len(validator.warnings) == 1

    def test_validate_unique_ids_no_duplicates(self) -> None:
        """Distinct IDs across distinct files: no error."""
        p1 = Project(
            id="P001", title="a", status=Status.PLANNING, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        p2 = Project(
            id="P002", title="b", status=Status.PLANNING, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        files = {
            "plan/projects/P001-a.md": PlanFile(entity=p1),
            "plan/projects/P002-b.md": PlanFile(entity=p2),
        }
        validator = SchemaValidator()
        assert validator.validate_unique_ids(files) is True
        assert len(validator.errors) == 0

    def test_validate_unique_ids_catches_duplicate(self) -> None:
        """Two different files claiming the same ID: an error naming both files."""
        p1 = Project(
            id="P001", title="original", status=Status.PLANNING, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        p2 = Project(
            id="P001", title="collides with the above", status=Status.PLANNING, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        files = {
            "plan/projects/P001-original.md": PlanFile(entity=p1),
            "plan/projects/P001-renamed-but-not-really.md": PlanFile(entity=p2),
        }
        validator = SchemaValidator()
        assert validator.validate_unique_ids(files) is False
        assert len(validator.errors) == 1
        error = validator.errors[0]
        assert error.entity_id == "P001"
        assert "P001-original.md" in error.message
        assert "P001-renamed-but-not-really.md" in error.message

    def test_validate_unique_ids_skips_parse_errors(self) -> None:
        """A file that failed to parse (dict with 'error') isn't treated as an entity."""
        p1 = Project(
            id="P001", title="a", status=Status.PLANNING, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        files = {
            "plan/projects/P001-a.md": PlanFile(entity=p1),
            "plan/projects/broken.md": {"error": "malformed YAML"},
        }
        validator = SchemaValidator()
        assert validator.validate_unique_ids(files) is True

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
