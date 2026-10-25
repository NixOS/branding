"""Element-aligned numeric comparison of two parsed SVG line lists.

Lines come from `parse.parse_node`. Numbers are masked, the masked lines
are aligned with difflib, and deltas are measured only between lines that
align. Lines that do not align are counted, not measured: positional
pairing over a file with one inserted element would otherwise report a
meaningless delta.

Alignment is by masked text, so an inserted element whose masked lines
equal an existing element's is paired with it and its numbers are
measured. This is a drift detector for numerically changed files, not a
structural diff; a large delta is a prompt to look at the HTML report.
"""

import difflib
import re
from dataclasses import dataclass

NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
# parse_node's own tokens: the depth tag "@0/1/3>" on open and close lines and
# the index label "[0001]". They are masked so shifted siblings still align,
# but they are not measured: an inserted sibling renumbers every later one.
STRUCTURE = re.compile(r"@\d+(?:/\d+)*>|\[\d+\]")


def mask(line: str) -> str:
    return NUMBER.sub("#", line)


def numbers(line: str) -> list[float]:
    return [float(match) for match in NUMBER.findall(STRUCTURE.sub("", line))]


@dataclass(frozen=True)
class NumericResult:
    matched: int
    unmatched_before: int
    unmatched_after: int
    compared: int  # numbers compared on matched lines
    changed: int  # of those, how many differ
    max_delta: float


def compare_numeric(before: list[str], after: list[str]) -> NumericResult:
    matcher = difflib.SequenceMatcher(
        a=[mask(line) for line in before],
        b=[mask(line) for line in after],
        autojunk=False,
    )
    matched = 0
    unmatched_before = 0
    unmatched_after = 0
    compared = 0
    changed = 0
    max_delta = 0.0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            unmatched_before += i2 - i1
            unmatched_after += j2 - j1
            continue
        for line_before, line_after in zip(before[i1:i2], after[j1:j2], strict=True):
            for x, y in zip(numbers(line_before), numbers(line_after), strict=True):
                compared += 1
                if x != y:
                    changed += 1
                    max_delta = max(max_delta, abs(x - y))
            matched += 1
    return NumericResult(
        matched, unmatched_before, unmatched_after, compared, changed, max_delta
    )
