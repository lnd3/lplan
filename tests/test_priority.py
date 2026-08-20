"""Tests for priority scoring engine."""

from datetime import date
import pytest
from planner.models import Project, Status, Priority
from planner.priority import PriorityEngine


class TestPriorityEngine:
    """Test PriorityEngine."""

    def test_score_to_priority_high(self) -> None:
        """Test score >= 2.0 maps to HIGH."""
        engine = PriorityEngine()
        assert engine.score_to_priority(2.0) == Priority.HIGH
        assert engine.score_to_priority(2.5) == Priority.HIGH
        assert engine.score_to_priority(3.0) == Priority.HIGH

    def test_score_to_priority_medium(self) -> None:
        """Test 1.0 <= score < 2.0 maps to MEDIUM."""
        engine = PriorityEngine()
        assert engine.score_to_priority(1.0) == Priority.MEDIUM
        assert engine.score_to_priority(1.5) == Priority.MEDIUM
        assert engine.score_to_priority(1.9) == Priority.MEDIUM

    def test_score_to_priority_low(self) -> None:
        """Test score < 1.0 maps to LOW."""
        engine = PriorityEngine()
        assert engine.score_to_priority(0.0) == Priority.LOW
        assert engine.score_to_priority(0.5) == Priority.LOW
        assert engine.score_to_priority(0.9) == Priority.LOW
        assert engine.score_to_priority(-0.5) == Priority.LOW

    def test_compute_score_single_driver(self) -> None:
        """Test computing score from single driver."""
        engine = PriorityEngine()
        score = engine.compute_score(["strategic_edge"])
        assert score == 1.0

    def test_compute_score_multiple_drivers(self) -> None:
        """Test computing score from multiple drivers."""
        engine = PriorityEngine()
        score = engine.compute_score(["strategic_edge", "improves_active"])
        assert score == 2.5

    def test_compute_score_negative_driver(self) -> None:
        """Test computing score with negative driver."""
        engine = PriorityEngine()
        score = engine.compute_score(["strategic_edge", "blocked_on_infrastructure"])
        assert score == -1.5

    def test_compute_score_unknown_driver(self) -> None:
        """Test that unknown drivers are ignored."""
        engine = PriorityEngine()
        score = engine.compute_score(["strategic_edge", "unknown_driver"])
        assert score == 1.0  # Unknown driver is ignored

    def test_deferred_wait_driver(self) -> None:
        """Test deferred_wait_* driver pattern."""
        engine = PriorityEngine()
        score = engine.compute_score(["strategic_edge", "deferred_wait_P001"])
        assert score == -1.0  # 1.0 + (-2.0)

    def test_analyze_project_match(self) -> None:
        """Test project analysis when computed priority matches declared."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.HIGH,
            priority_drivers=["critical_live_path_only"],  # +2.5 -> HIGH
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        engine = PriorityEngine()
        analysis = engine.analyze_project(project)

        assert analysis["match"] is True
        assert analysis["computed_priority"] == "HIGH"
        assert analysis["declared_priority"] == "HIGH"
        assert analysis["score"] == 2.5

    def test_analyze_project_mismatch(self) -> None:
        """Test project analysis when computed priority doesn't match declared."""
        project = Project(
            id="P001",
            title="Test",
            status=Status.PLANNING,
            priority=Priority.MEDIUM,  # Declared as MEDIUM
            priority_drivers=["critical_live_path_only"],  # +2.5 -> HIGH (mismatch!)
            created=date(2026, 8, 20),
            updated=date(2026, 8, 20),
        )
        engine = PriorityEngine()
        analysis = engine.analyze_project(project)

        assert analysis["match"] is False
        assert analysis["computed_priority"] == "HIGH"
        assert analysis["declared_priority"] == "MEDIUM"

    def test_custom_drivers(self) -> None:
        """Test engine with custom drivers."""
        custom = {"regulatory_compliance": 2.0}
        engine = PriorityEngine(custom_drivers=custom)

        score = engine.compute_score(["regulatory_compliance"])
        assert score == 2.0

    def test_custom_drivers_override_core(self) -> None:
        """Test that custom drivers can override core drivers."""
        custom = {"strategic_edge": 2.0}  # Override from 1.0 to 2.0
        engine = PriorityEngine(custom_drivers=custom)

        score = engine.compute_score(["strategic_edge"])
        assert score == 2.0

    def test_is_driver_valid(self) -> None:
        """Test driver validation."""
        engine = PriorityEngine()

        assert engine.is_driver_valid("strategic_edge") is True
        assert engine.is_driver_valid("deferred_wait_P001") is True
        assert engine.is_driver_valid("unknown_driver") is False

    def test_get_driver_weights(self) -> None:
        """Test getting all driver weights."""
        engine = PriorityEngine()
        weights = engine.get_driver_weights()

        assert "strategic_edge" in weights
        assert weights["strategic_edge"] == 1.0
        assert "critical_live_path_only" in weights
        assert weights["critical_live_path_only"] == 2.5
