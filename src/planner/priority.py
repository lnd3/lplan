"""Priority scoring engine based on drivers."""

from typing import Dict, List, Tuple, Optional
from .models import Project, Priority


class PriorityEngine:
    """Compute priority from priority drivers."""

    # Core framework drivers and their weights
    CORE_DRIVERS: Dict[str, float] = {
        "critical_live_path_only": 2.5,
        "live_critical": 2.0,
        "improves_active": 1.5,
        "enables_multiple": 1.5,
        "strategic_edge": 1.0,
        "improves_accuracy": 1.0,
        "technical_debt": 0.5,
        "blocked_on_infrastructure": -2.5,
    }

    # Pattern for deferred drivers: deferred_wait_* = -2.0
    DEFERRED_WAIT_WEIGHT = -2.0

    def __init__(self, custom_drivers: Optional[Dict[str, float]] = None):
        """Initialize engine with optional custom drivers.

        Args:
            custom_drivers: Dict mapping driver name to weight. Merged with core drivers.
        """
        self.drivers = self.CORE_DRIVERS.copy()
        if custom_drivers:
            self.drivers.update(custom_drivers)

    def compute_score(self, priority_drivers: List[str]) -> float:
        """Compute priority score from driver list.

        Args:
            priority_drivers: List of driver keys

        Returns:
            Computed score (sum of driver weights)
        """
        score = 0.0
        for driver in priority_drivers:
            if driver in self.drivers:
                score += self.drivers[driver]
            elif driver.startswith("deferred_wait_"):
                score += self.DEFERRED_WAIT_WEIGHT
            # Unknown drivers are ignored (could add warning here)

        return score

    def score_to_priority(self, score: float) -> Priority:
        """Map score to priority level.

        Args:
            score: Computed priority score

        Returns:
            Priority enum value

        Rules:
        - score >= 2.0: HIGH
        - 1.0 <= score < 2.0: MEDIUM
        - 0 <= score < 1.0: LOW
        - score < 0: LOW (but status should be BLOCKED)
        """
        if score >= 2.0:
            return Priority.HIGH
        elif score < 0:
            return Priority.LOW  # Status=BLOCKED takes precedence
        elif score < 1.0:
            return Priority.LOW
        else:
            return Priority.MEDIUM

    def compute_priority(self, priority_drivers: List[str]) -> Priority:
        """Compute priority from drivers in one call."""
        score = self.compute_score(priority_drivers)
        return self.score_to_priority(score)

    def analyze_project(self, project: Project) -> Dict[str, object]:
        """Analyze project priority with detailed breakdown.

        Returns dict with:
        - score: computed score
        - priority: computed priority
        - declared_priority: project's declared priority
        - match: whether computed == declared
        - driver_contributions: dict of driver -> weight
        - unknown_drivers: list of drivers not in framework
        """
        score = self.compute_score(project.priority_drivers)
        computed_priority = self.score_to_priority(score)

        driver_contributions: Dict[str, float] = {}
        unknown_drivers: List[str] = []

        for driver in project.priority_drivers:
            if driver in self.drivers:
                driver_contributions[driver] = self.drivers[driver]
            elif driver.startswith("deferred_wait_"):
                driver_contributions[driver] = self.DEFERRED_WAIT_WEIGHT
            else:
                unknown_drivers.append(driver)

        return {
            "project_id": project.id,
            "score": score,
            "computed_priority": computed_priority.value,
            "declared_priority": project.priority.value,
            "match": computed_priority == project.priority,
            "driver_contributions": driver_contributions,
            "unknown_drivers": unknown_drivers,
            "status": project.status.value,
        }

    def get_driver_weights(self) -> Dict[str, float]:
        """Get all defined driver weights."""
        return self.drivers.copy()

    def is_driver_valid(self, driver: str) -> bool:
        """Check if driver is defined in framework."""
        return driver in self.drivers or driver.startswith("deferred_wait_")
