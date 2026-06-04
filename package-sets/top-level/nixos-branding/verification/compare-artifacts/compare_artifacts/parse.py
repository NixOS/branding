"""Pure SVG → list[str] parsers."""

import math
import re
from collections.abc import Sequence
from itertools import batched

INDENTAMOUNT = 2
INDENTCHAR = " "
INDENT = INDENTAMOUNT * INDENTCHAR


def pad_min(seq: Sequence, min: int = 4) -> int:
    """Return enough width to label `len(seq)` items, never less than `min`.

    Used by the parsers that produce indexed labels like `[0001] M 10 20`.
    """
    if len(seq) == 0:
        return min
    return max(min, math.ceil(math.log10(len(seq))))


def no_name_space(tag: str) -> str:
    """Strip an XML namespace prefix from a tag name.

    `{http://www.w3.org/2000/svg}svg` → `svg`.
    """
    _, _, only_tag = tag.rpartition("}")
    return only_tag


def parse_misc(indent: str, name: str, value: str) -> str:
    """Render a generic XML attribute as `@name: value`."""
    return f"{indent}@{name}: {value}"


def parse_viewbox(indent: str, name: str, value: str) -> list[str]:
    """Render a `viewBox="x y w h"` attribute as one indexed line per value."""
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    parts = value.split()
    pad = pad_min(parts)
    for index, elem in enumerate(parts):
        parsed.append(f"{indent}[{index:0{pad}d}] {elem}")
    return parsed


def parse_d(indent: str, name: str, value: str) -> list[str]:
    """Render an SVG path `d="..."` attribute as one indexed line per command.

    The path string is split on alphabetic command letters (M, L, C, ...),
    each letter is paired with the following number sequence, and each
    pair is rendered as `[NNNN] X 1 2 3 ...`.
    """
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    parts = re.split(r"([a-zA-Z]+)", value)
    parts = list(filter(None, parts))
    pairs = list(batched(parts, 2))
    pad = pad_min(pairs)
    for index, elem in enumerate(pairs):
        # batched may yield 1-tuples on a trailing letter; guard with a fallback.
        if len(elem) == 2:
            parsed.append(f"{indent}[{index:0{pad}d}] {elem[0]} {elem[1].strip()}")
        else:
            parsed.append(f"{indent}[{index:0{pad}d}] {elem[0]} ")
    return parsed
