"""Writer module for updating plan file frontmatter and content."""

from datetime import date
from pathlib import Path
from typing import Dict, Any
import yaml


def update_entity_frontmatter(filepath: Path, updates: Dict[str, Any]) -> None:
    """Update frontmatter fields in a plan file.

    Reads file, parses YAML frontmatter, merges updates, preserves body content.

    Args:
        filepath: Path to the plan file
        updates: Dict of fields to update (e.g., {"status": "DONE", "updated": date.today()})

    Raises:
        ValueError: If file doesn't have valid frontmatter
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        raise ValueError(f"File {filepath} does not start with frontmatter delimiter")

    # Split on the closing --- delimiter
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"File {filepath} has malformed frontmatter (no closing ---)")

    frontmatter_str = parts[1]
    body = parts[2]

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {filepath}: {e}")

    if not isinstance(frontmatter, dict):
        raise ValueError(f"Frontmatter in {filepath} is not a YAML object")

    # Merge updates
    frontmatter.update(updates)

    # Re-serialize YAML (preserve key order where possible)
    new_frontmatter = yaml.dump(
        frontmatter,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        default_style=None,
    )

    # Write back
    new_content = f"---\n{new_frontmatter}---{body}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


def append_log_entry(filepath: Path, note: str, entry_date: date = None) -> None:
    """Append an entry to the Log section of a plan file.

    Finds the ## Log section, or creates it at the end. Prepends new entry (most-recent-first).

    Args:
        filepath: Path to the plan file
        note: The log entry text
        entry_date: Date for the log entry (default: today)
    """
    if entry_date is None:
        entry_date = date.today()

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter from body
    if not content.startswith("---"):
        raise ValueError(f"File {filepath} does not start with frontmatter delimiter")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"File {filepath} has malformed frontmatter")

    frontmatter = parts[1]
    body = parts[2]

    # Look for ## Log section
    log_marker = "## Log"
    if log_marker in body:
        # Find the position and insert after the header
        log_pos = body.index(log_marker)
        # Find the end of the line
        line_end = body.index("\n", log_pos)
        # Insert new entry after the heading
        new_entry = f"\n{entry_date.isoformat()} — {note}"
        # Check if there's already content after ## Log
        after_header = body[line_end + 1 :].lstrip("\n")
        if after_header.strip():
            # There's content, insert before it
            new_body = (
                body[: line_end + 1]
                + new_entry
                + "\n"
                + body[line_end + 1 :]
            )
        else:
            # No content yet, just append
            new_body = body + new_entry + "\n"
    else:
        # No ## Log section, create one at the end
        new_body = body.rstrip() + f"\n\n## Log\n\n{entry_date.isoformat()} — {note}\n"

    # Write back
    new_content = f"---{frontmatter}---{new_body}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
