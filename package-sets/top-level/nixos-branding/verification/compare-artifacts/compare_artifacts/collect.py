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
