"""Companion file detection for the D005 template-file-family convention.

A template-instantiated root file (e.g. `D005-template-file-family-scaling.md`,
`FOCUS.md`) may have companion files beside it: `{root}_{suffix}.md`. Entity
and root files always use hyphens in their names; companions are the only
`.md` files under `plan/` whose stem contains an underscore, so that's the
whole detection rule.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

CANONICAL_SUFFIXES = ("extension", "tmp", "learnings", "history")


def is_companion_file(filepath: Path) -> bool:
    """True if `filepath` is a companion (not a template-shaped root/entity file)."""
    return "_" in filepath.stem


def companion_suffix(filepath: Path) -> str:
    """The suffix after the root's last underscore, e.g. 'learnings' for D005_learnings.md."""
    return filepath.stem.rsplit("_", 1)[-1]


def companion_root_stem(filepath: Path) -> str:
    """The root name a companion belongs to, e.g. 'D005' for D005_learnings.md."""
    return filepath.stem.rsplit("_", 1)[0]


def find_companions(root_filepath: Path) -> List[Path]:
    """All companion files sitting beside `root_filepath` in the same directory."""
    root_stem = root_filepath.stem
    directory = root_filepath.parent
    if not directory.exists():
        return []
    return sorted(
        p for p in directory.glob(f"{root_stem}_*.md")
        if is_companion_file(p)
    )
