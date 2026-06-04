"""Pure SVG → list[str] parsers."""

import math
from collections.abc import Sequence

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
