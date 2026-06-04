"""Pure SVG → list[str] parsers."""

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
    return max(min, len(str(len(seq))))
