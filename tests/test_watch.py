"""Tests for watch.py module."""

from datetime import date

import pytest

from planner.models import Project, Status, Priority
from planner.watch import _detect_changes


def test_detect_changes_status_transition():
    """Test detection of status changes."""
    current = {
        "P001": {"status": "IN_PROGRESS", "priority": "HIGH", "depends": []},
    }

    previous = {
        "P001": {"status": "PLANNING", "priority": "HIGH", "depends": []},
    }

    messages = []
    _detect_changes(current, previous, lambda msg: messages.append(msg))

    assert len(messages) > 0
    assert any("IN_PROGRESS" in msg for msg in messages)


def test_detect_changes_blocked_status():
    """Test that BLOCKED transition is specially flagged."""
    current = {
        "P001": {"status": "BLOCKED", "priority": "HIGH", "depends": []},
    }

    previous = {
        "P001": {"status": "IN_PROGRESS", "priority": "HIGH", "depends": []},
    }

    messages = []
    _detect_changes(current, previous, lambda msg: messages.append(msg))

    assert len(messages) > 0
    assert any("BLOCKED" in msg and "⚠" in msg for msg in messages)


def test_detect_changes_new_project():
    """Test detection of new projects."""
    current = {
        "P002": {"status": "PLANNING", "priority": "HIGH", "depends": []},
    }

    previous = {}

    messages = []
    _detect_changes(current, previous, lambda msg: messages.append(msg))

    assert len(messages) > 0
    assert any("P002" in msg and "New" in msg for msg in messages)


def test_detect_changes_removed_project():
    """Test detection of removed projects."""
    current = {}

    previous = {
        "P001": {"status": "PLANNING", "priority": "HIGH", "depends": []},
    }

    messages = []
    _detect_changes(current, previous, lambda msg: messages.append(msg))

    assert len(messages) > 0
    assert any("P001" in msg and "removed" in msg for msg in messages)


def test_detect_changes_priority_change():
    """Test detection of priority changes."""
    current = {
        "P001": {"status": "PLANNING", "priority": "MEDIUM", "depends": []},
    }

    previous = {
        "P001": {"status": "PLANNING", "priority": "HIGH", "depends": []},
    }

    messages = []
    _detect_changes(current, previous, lambda msg: messages.append(msg))

    assert len(messages) > 0
    assert any("priority" in msg.lower() for msg in messages)


def test_detect_changes_no_changes():
    """Test that no changes produces no messages."""
    snapshot = {
        "P001": {"status": "PLANNING", "priority": "HIGH", "depends": []},
    }

    messages = []
    _detect_changes(snapshot, snapshot.copy(), lambda msg: messages.append(msg))

    assert len(messages) == 0
