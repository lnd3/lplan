"""Tests for status_overview.py -- specifically collect_validator_warnings(),
added to close the gap where the Plan Health Dashboard's needs-attention panel
only surfaced check-refs findings and never ran the full SchemaValidator (so
A027's parent-child consistency check and D008's phase-anchor check were
invisible in the live dashboard even though `plan validate` showed them).
"""

from datetime import date
from pathlib import Path

from planner.graph import DependencyGraph
from planner.models import Action, Design, MasterPlan, PlanFile, Project, Status, Priority
from planner.status_overview import (
    collect_validator_warnings, compute_status_overview, master_plan_rollup, project_rollup,
)


def _project(id_, status, phase_body=None):
    p = Project(
        id=id_, title=f"Title {id_}", status=status, priority=Priority.HIGH,
        priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
    )
    plan_file = PlanFile(entity=p, raw_content=phase_body or "")
    return p, plan_file


class TestProjectRollup:
    """project_rollup() should prefer the project's own Tasks/Phases checkboxes
    over child Design/Action DONE-counts, since the child set grows as work
    gets discovered mid-flight (mostly upward) and drifts away from actual
    progress in a way deliberate checkboxes don't."""

    def test_prefers_checkboxes_over_children(self) -> None:
        # Checkboxes say 75% done; children (if used) would say 100% (1/1 DONE).
        # These must disagree for the test to prove which one actually wins.
        raw = "## Tasks\n\n- [x] a\n- [x] b\n- [x] c\n- [ ] d\n"
        project, plan_file = _project("P001", Status.IN_PROGRESS, phase_body=raw)
        design = Design(
            id="D001", title="d", status=Status.DONE, project="P001",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )

        result = project_rollup(project, {"D001": design}, {}, plan_file=plan_file)

        assert result["pct_source"] == "checkboxes"
        assert result["pct_done"] == 75
        assert result["checkbox_done"] == 3
        assert result["checkbox_total"] == 4
        # Child counts still reported as context, just not driving pct_done.
        assert result["child_count"] == 1
        assert result["child_done"] == 1

    def test_falls_back_to_children_when_no_checkboxes(self) -> None:
        project, plan_file = _project("P001", Status.IN_PROGRESS, phase_body="## Goal\n\nNo tasks here.\n")
        design = Design(
            id="D001", title="d", status=Status.DONE, project="P001",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        action = Action(
            id="A001", title="a", status=Status.IN_PROGRESS, project="P001",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )

        result = project_rollup(project, {"D001": design}, {"A001": action}, plan_file=plan_file)

        assert result["pct_source"] == "children"
        assert result["pct_done"] == 50  # 1/2 children DONE

    def test_falls_back_to_status_when_nothing_available(self) -> None:
        project, _ = _project("P001", Status.DONE)

        result = project_rollup(project, {}, {}, plan_file=None)

        assert result["pct_source"] == "status"
        assert result["pct_done"] == 100
        assert result["no_children"] is True


class TestMasterPlanRollup:
    def test_prefers_checkboxes_over_child_projects(self) -> None:
        raw = "## Tasks\n\n- [x] a\n- [ ] b\n"  # 50%
        mp = MasterPlan(
            id="M001", title="m", status=Status.IN_PROGRESS, stakeholder="eng",
            created=date(2026, 8, 20), updated=date(2026, 8, 20),
        )
        plan_file = PlanFile(entity=mp, raw_content=raw)
        # Child project is DONE (would be 100% under the old child-count math).
        project = Project(
            id="P001", title="p", status=Status.DONE, priority=Priority.HIGH,
            priority_drivers=["strategic_edge"], created=date(2026, 8, 20), updated=date(2026, 8, 20),
            parent_master_plan=["M001"],
        )

        result = master_plan_rollup(mp, {"P001": project}, plan_file=plan_file)

        assert result["pct_source"] == "checkboxes"
        assert result["pct_done"] == 50
        assert result["child_count"] == 1
        assert result["child_done"] == 1


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


class TestComputeStatusOverviewSortOrder:
    """The Status dashboard's rollup lists should be least-complete-first."""

    def test_project_rollups_sorted_by_completion_ascending(self):
        projects = {}
        plan_files_by_id = {}
        for pid, checked in [("P001", 0), ("P002", 4), ("P003", 2)]:
            raw = "## Tasks\n\n" + "\n".join(
                f"- [{'x' if i < checked else ' '}] task {i}" for i in range(4)
            )
            project, plan_file = _project(pid, Status.IN_PROGRESS, phase_body=raw)
            projects[pid] = project
            plan_files_by_id[pid] = plan_file

        graph = DependencyGraph(projects)
        data = compute_status_overview(
            {}, {}, {}, projects, {}, {}, plan_files_by_id, graph, Path("."),
        )

        ids_in_order = [r["id"] for r in data["project_rollups"]]
        # P001 (0%) least complete, P003 (50%), P002 (100%) most complete.
        assert ids_in_order == ["P001", "P003", "P002"]
