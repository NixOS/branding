"""File pairing and DiffSpec.

This module owns the single I/O boundary into the SVG parser:
`path_to_parsed` reads an SVG file from disk and hands its parsed root
to `compare_artifacts.parse.parse_node`. Everything else in `parse.py`
stays pure.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from compare_artifacts.parse import parse_node


@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path  # relative to the build output root
    state: Literal["added", "removed", "changed", "unchanged"]


def path_to_parsed(root: Path, rel: Path) -> list[str]:
    """Read the SVG at `root / rel` and return its parsed line representation."""
    return parse_node(ET.fromstring((root / rel).read_text()), [])


def glob_path_no_parent(root: Path, glob: str) -> set[Path]:
    """Return all relative paths under `root` matching `glob`.

    Symlinks are followed so build outputs that link into the Nix store
    are walked transparently.
    """
    return {
        rpath.relative_to(root) for rpath in root.rglob(glob, recurse_symlinks=True)
    }


def collect_files(before_root: Path, after_root: Path) -> list[DiffSpec]:
    """Pair SVG files between two artifact trees and classify each pair.

    Returns one `DiffSpec` per file appearing in either tree, sorted by
    relative path. Includes `unchanged` specs so callers can show summary
    counts; filtering them out is the caller's responsibility.
    """
    before_files = glob_path_no_parent(before_root, "*.svg")
    after_files = glob_path_no_parent(after_root, "*.svg")
    all_files = sorted(before_files | after_files)
    diff_specs: list[DiffSpec] = []

    for path in all_files:
        match (path in before_files, path in after_files):
            case (True, True):
                before = path_to_parsed(before_root, path)
                after = path_to_parsed(after_root, path)
                state = "unchanged" if before == after else "changed"
            case (True, False):
                before = path_to_parsed(before_root, path)
                after = []
                state = "removed"
            case (False, True):
                before = []
                after = path_to_parsed(after_root, path)
                state = "added"
            case _:
                # Cannot happen — `all_files` is the union, so each path
                # is in at least one of the sets.
                raise AssertionError(f"unreachable: {path}")

        diff_specs.append(DiffSpec(before=before, after=after, path=path, state=state))

    return diff_specs


def counts(specs: list[DiffSpec]) -> dict[str, int]:
    """Return the count of specs in each of the four states.

    Always returns a dict with exactly four keys (`changed`, `added`,
    `removed`, `unchanged`) with integer values. Used by `report.py`
    for the on-page summary and by `cli.py`'s `--summary` flag for the
    JSON sidecar that CI consumes.
    """
    result = {"changed": 0, "added": 0, "removed": 0, "unchanged": 0}
    for spec in specs:
        result[spec.state] += 1
    return result
