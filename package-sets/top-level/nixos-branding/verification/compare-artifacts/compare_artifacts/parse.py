"""Pure SVG → list[str] parsers."""

import math
import re
from collections.abc import Sequence
from itertools import batched
from xml.etree.ElementTree import Element

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


def parse_points(indent: str, name: str, value: str) -> list[str]:
    """Render a `points="x1 y1 x2 y2 ..."` attribute as one indexed pair per line."""
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    pairs = list(batched(value.split(), 2))
    pad = pad_min(pairs)
    for index, elem in enumerate(pairs):
        parsed.append(f"{indent}[{index:0{pad}d}] ({elem[0]}, {elem[1]})")
    return parsed


def split_transforms(transform_str: str) -> list[str]:
    """Split an SVG `transform` attribute into individual function calls."""
    # `[a-zA-Z]+\([^)]*\)` matches:
    #   - [a-zA-Z]+   the function name (translate, rotate, ...)
    #   - \([^)]*\)   everything inside the parentheses
    pattern = r"[a-zA-Z]+\([^)]*\)"
    return re.findall(pattern, transform_str)


def parse_transform(indent: str, name: str, value: str) -> list[str]:
    """Render a `transform="..."` attribute as one function call per line."""
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    for part in split_transforms(value):
        parsed.append(f"{indent}{part}")
    return parsed


def parse_attributes(node: Element, parsed: list[str], indent: str) -> None:
    """Dispatch each attribute on `node` to the appropriate parser.

    Mutates `parsed` in place by appending one or more lines per attribute.
    The dispatching is intentionally hard-coded: each named SVG attribute
    has a render that produces more readable output than `parse_misc`.
    """
    indent += INDENT
    for name, value in node.attrib.items():
        match name:
            case "d":
                parsed.extend(parse_d(indent, name, value))
            case "points":
                parsed.extend(parse_points(indent, name, value))
            case "transform":
                parsed.extend(parse_transform(indent, name, value))
            case "viewBox":
                parsed.extend(parse_viewbox(indent, name, value))
            case _:
                parsed.append(parse_misc(indent, name, value))
