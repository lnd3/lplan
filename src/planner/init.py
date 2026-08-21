"""Plan directory initialization and scaffolding."""

from datetime import date
from pathlib import Path
from typing import Optional
import re
from .models import Project, Status, Priority


def _slugify(text: str) -> str:
    """Convert text to URL slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def init_plan(
    plan_dir: Path,
    repo_name: str,
    first_project_title: Optional[str] = None,
) -> None:
    """Initialize a new plan directory structure.

    Creates:
    - projects/, designs/, actions/ subdirectories
    - INDEX.md and CHANGELOG.md from templates
    - Optional P001-<slug>.md project file

    Args:
        plan_dir: Path to plan directory (created if needed)
        repo_name: Repository name (used in INDEX)
        first_project_title: Optional title for initial project (P001)
    """
    plan_dir = Path(plan_dir)
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    for subdir in ["projects", "designs", "actions"]:
        (plan_dir / subdir).mkdir(exist_ok=True)

    # Create INDEX.md if not present
    index_path = plan_dir / "INDEX.md"
    if not index_path.exists():
        today = date.today().isoformat()
        index_content = f"""# {repo_name} Plan Index

*Last updated: {today}*

Status: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

---

## Projects

| ID | Title | Status | Priority | Key Open Work |
| --- | --- | --- | --- | --- |

---

## Designs

| ID | Title | Status | Project | Doc |
| --- | --- | --- | --- | --- |

---

## Actions

| ID | Title | Status | Design | Open Tasks |
| --- | --- | --- | --- | --- |
"""
        index_path.write_text(index_content, encoding="utf-8")

    # Create CHANGELOG.md if not present
    changelog_path = plan_dir / "CHANGELOG.md"
    if not changelog_path.exists():
        changelog_content = """# Plan Changelog

Append-only record of all status and priority changes.

Format: `YYYY-MM-DD | ID | old_status → new_status | note`

---

"""
        changelog_path.write_text(changelog_content, encoding="utf-8")

    # Create VALIDATION.md if not present
    validation_path = plan_dir / "VALIDATION.md"
    if not validation_path.exists():
        # Read template
        template_path = Path(__file__).parent.parent.parent / "templates" / "VALIDATION.md.template"
        if template_path.exists():
            validation_content = template_path.read_text(encoding="utf-8")
        else:
            # Fallback if template not found
            validation_content = """# Plan Validation

This plan uses the [lplan](https://github.com/lnd3/lplan) framework for structured project management.

## Validation Requirement

Before committing changes to `plan/` directory, always validate:

```bash
./deps/lplan/bin/plan validate ./plan
```

Expected output:
```
✓ Validation passed (N entities)
(0 warnings)
```

See `deps/lplan/README.md` and `deps/lplan/QUICK_REFERENCE.md` for complete documentation.
"""
        validation_path.write_text(validation_content, encoding="utf-8")

    # Optionally create initial project
    if first_project_title:
        today = date.today().isoformat()
        slug = _slugify(first_project_title)
        project_file = plan_dir / "projects" / f"P001-{slug}.md"

        # Only create if P001-* doesn't already exist
        existing_p001 = list(plan_dir.glob("projects/P001-*.md"))
        if not existing_p001:
            project_content = f"""---
id: P001
title: {first_project_title}
status: IDEA
priority: MEDIUM
priority_drivers:
  - strategic_edge
created: {today}
updated: {today}
depends: []
external_dependencies: []
enables: []
---

## Goal

1–2 paragraph statement of what this project achieves. What problem does it solve? Why is it important?

## Scope

Bullet-point list of what's included and excluded:
- Component A
- Component B
- Not included: X, Y, Z

## Linked

- **Projects**: (other projects this depends on or relates to)
- **Designs**: (designs that specify this project)
- **Actions**: (concrete task lists)
- **Dependencies**: (upstream repos/features)

## Tasks

### Phase 1
- [ ] Task A
- [ ] Task B

### Phase 2
- [ ] Task C
- [ ] Task D

## Log

{today} — Project created.
"""
            project_file.write_text(project_content, encoding="utf-8")

    # Create README.md if not present
    readme_path = plan_dir / "README.md"
    if not readme_path.exists():
        template_path = Path(__file__).parent.parent.parent / "templates" / "README.md.template"
        if template_path.exists():
            readme_content = template_path.read_text(encoding="utf-8")
        else:
            readme_content = f"""# {repo_name} Planning System

This directory contains the planning structure for {repo_name}, following the lplan generic planning framework.

## Quick Start

```bash
./deps/lplan/bin/plan validate ./plan    # Validate plan before commit
cat plan/INDEX.md                          # View current status
```

See `deps/lplan/README.md` for full documentation.
"""
        readme_path.write_text(readme_content, encoding="utf-8")

    # Create FOCUS.md if not present
    focus_path = plan_dir / "FOCUS.md"
    if not focus_path.exists():
        template_path = Path(__file__).parent.parent.parent / "templates" / "FOCUS.md.template"
        if template_path.exists():
            focus_content = template_path.read_text(encoding="utf-8")
        else:
            focus_content = """# Focus

*Rewritten each session. Not append-only — reflects current state only.*

---

## Active

*(What is being worked on right now and why)*

---

## Blocked

*(What cannot proceed and what is needed to unblock it)*

---

## Next

*(Ordered list of the next 2–4 concrete steps after active work completes)*
"""
        focus_path.write_text(focus_content, encoding="utf-8")

    # Create REFLECTION.md if not present
    reflection_path = plan_dir / "REFLECTION.md"
    if not reflection_path.exists():
        template_path = Path(__file__).parent.parent.parent / "templates" / "REFLECTION.md.template"
        if template_path.exists():
            reflection_content = template_path.read_text(encoding="utf-8")
        else:
            reflection_content = """# Reflection

Append-only log of learnings, gotchas, and patterns discovered during development.
Not session notes — these are stable insights worth carrying forward indefinitely.

Format: `YYYY-MM-DD | CATEGORY | insight`
Categories: GOTCHA · PATTERN · LEARNING · WARNING · DECISION

---

"""
        reflection_path.write_text(reflection_content, encoding="utf-8")
