"""Tests for status_overview.py -- specifically collect_validator_warnings(),
added to close the gap where the Plan Health Dashboard's needs-attention panel
only surfaced check-refs findings and never ran the full SchemaValidator (so
A027's parent-child consistency check and D008's phase-anchor check were
invisible in the live dashboard even though `plan validate` showed them).
"""

from datetime import date

from planner.models import Action, Design, PlanFile, Project, Status, Priority
from planner.status_overview import collect_validator_warnings


def _project(id_, status, phase_body=None):
    p = Project(
        id=id_, title=f"Title {id_}", status=status, priority=Priority.HIGH,
        priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
    )
    plan_file = PlanFile(entity=p, raw_content=phase_body or "")
    return p, plan_file


class TestCollectValidatorWarnings:
    def test_done_project_with_open_child_surfaces(self):
        """A027's check reaches the dashboard payload, not just the CLI."""
        project, project_file = _project("P001", Status.DONE)
        action = Action(
            id="A001", title="Open work", status=Status.IN_PROGRESS, project="P001",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        entities_by_id = {"P001": project, "A001": action}
        plan_files_by_id = {"P001": project_file}

        warnings = collect_validator_warnings(entities_by_id, {"P001": project}, plan_files_by_id)

        assert any(w["id"] == "P001" and "A001" in w["message"] for w in warnings)
        p001_warning = next(w for w in warnings if w["id"] == "P001")
        assert p001_warning["type"] == "project"

    def test_clean_plan_produces_no_warnings(self):
        """A project with no dangling refs, no status inconsistency, no unanchored phases is silent."""
        project, project_file = _project("P001", Status.IN_PROGRESS)
        entities_by_id = {"P001": project}
        plan_files_by_id = {"P001": project_file}

        warnings = collect_validator_warnings(entities_by_id, {"P001": project}, plan_files_by_id)

        assert warnings == []

    def test_unanchored_phase_surfaces(self):
        """D008's phase-anchor check also reaches the dashboard payload."""
        raw = "## Phases\n\n### Phase 1 -- No anchor\n- [ ] a task\n"
        project, project_file = _project("P001", Status.IN_PROGRESS, phase_body=raw)
        entities_by_id = {"P001": project}
        plan_files_by_id = {"P001": project_file}

        warnings = collect_validator_warnings(entities_by_id, {"P001": project}, plan_files_by_id)

        assert any(w["id"] == "P001" and "Design anchor" in w["message"] for w in warnings)

    def test_path_by_id_threaded_through(self):
        """Each warning carries a path when one is provided, for the dashboard's click-through."""
        project, project_file = _project("P001", Status.DONE)
        action = Action(
            id="A001", title="Open work", status=Status.IN_PROGRESS, project="P001",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        entities_by_id = {"P001": project, "A001": action}
        plan_files_by_id = {"P001": project_file}
        path_by_id = {"P001": "projects/P001-title.md"}

        warnings = collect_validator_warnings(entities_by_id, {"P001": project}, plan_files_by_id, path_by_id)

        p001_warning = next(w for w in warnings if w["id"] == "P001")
        assert p001_warning["path"] == "projects/P001-title.md"
