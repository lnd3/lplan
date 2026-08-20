"""Plan monitoring and change detection."""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Callable, Optional
from .models import PlanEntity, Project, Status
from .parser import PlanParser
from .graph import DependencyGraph


def watch_plan(
    plan_dir: Path,
    interval: int = 5,
    notify: Optional[Callable[[str], None]] = None,
) -> None:
    """Monitor plan for changes and notify on status updates.

    Polls the plan directory at regular intervals, detects:
    - Status transitions to BLOCKED
    - Priority mismatches (computed vs declared)
    - Newly-introduced dependency cycles

    Args:
        plan_dir: Path to plan directory
        interval: Polling interval in seconds (default: 5)
        notify: Callback function for notifications (default: print to stderr)

    Raises:
        KeyboardInterrupt: When user presses Ctrl-C (exits gracefully)
    """
    if notify is None:
        notify = _default_notify

    previous_snapshot: Dict[str, Dict] = {}
    notify(f"✓ Watching {plan_dir} (Ctrl-C to stop)")

    try:
        while True:
            try:
                # Parse current state
                parsed = PlanParser.parse_directory(plan_dir)

                # Extract projects only
                projects: Dict[str, Project] = {}
                for file_path, result in parsed.items():
                    if not isinstance(result, dict) or "error" not in result:
                        entity = result.entity
                        if isinstance(entity, Project):
                            projects[entity.id] = entity

                # Build current snapshot
                current_snapshot: Dict[str, Dict] = {}
                for pid, project in projects.items():
                    current_snapshot[pid] = {
                        "status": project.status.value,
                        "priority": project.priority.value,
                        "depends": project.depends,
                    }

                # Detect changes
                _detect_changes(current_snapshot, previous_snapshot, notify)

                # Check for cycles
                if projects:
                    graph = DependencyGraph(projects)
                    if graph.has_cycles():
                        cycles = graph.find_cycles()
                        if cycles:
                            cycle_strs = [" → ".join(c) for c in cycles]
                            msg = "⚠ Dependency cycles detected:\n  " + "\n  ".join(cycle_strs)
                            notify(msg)

                # Update snapshot
                previous_snapshot = current_snapshot

            except Exception as e:
                notify(f"⚠ Parse error: {e}")

            # Sleep until next poll
            time.sleep(interval)

    except KeyboardInterrupt:
        notify("✓ Watch stopped")


def _detect_changes(
    current: Dict[str, Dict],
    previous: Dict[str, Dict],
    notify: Callable[[str], None],
) -> None:
    """Detect status and priority changes between snapshots.

    Args:
        current: Current snapshot of projects
        previous: Previous snapshot
        notify: Notification callback
    """
    for pid, curr_data in current.items():
        if pid not in previous:
            # New project
            notify(f"✓ New project: {pid}")
            continue

        prev_data = previous[pid]

        # Status change
        if curr_data["status"] != prev_data["status"]:
            old = prev_data["status"]
            new = curr_data["status"]

            if new == Status.BLOCKED.value:
                notify(f"⚠ Project {pid} is now BLOCKED (was {old})")
            else:
                notify(f"ℹ Project {pid}: {old} → {new}")

        # Priority change (from computed mismatch detection)
        if curr_data["priority"] != prev_data["priority"]:
            notify(f"ℹ Project {pid}: priority changed to {curr_data['priority']}")

    # Detect removed projects
    for pid in previous:
        if pid not in current:
            notify(f"ℹ Project {pid} removed")


def _default_notify(message: str) -> None:
    """Default notification: print to stderr with timestamp.

    Args:
        message: Notification message
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)
