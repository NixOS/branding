import difflib
import html
import math
import re
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import batched
from pathlib import Path
from typing import Literal
from xml.etree.ElementTree import Element

INDENTAMOUNT = 2
INDENTCHAR = " "
INDENT = INDENTAMOUNT * INDENTCHAR

FIN0 = "./result-rerounded/"
FIN1 = "./result-rerounded2/"


@dataclass
class DiffSpec:
    before: list[str]
    after: list[str]
    path: Path
    state: Literal["added", "removed", "changed", "unchanged"]


class MultiHtmlDiff(difflib.HtmlDiff):
    def make_multi_file(self, diff_specs: list[DiffSpec], *, charset: str = "utf-8"):
        tables = []
        for spec in diff_specs:
            tables.append(
                f"<h2>{html.escape(str(spec.path))} {spec.state}</h2>\n"
                + self.make_table(
                    spec.before, spec.after, f"{spec.path} (old)", f"{spec.path} (new)"
                )
            )

        body_tables = "\n<hr />\n".join(tables)

        return self._file_template % {
            "styles": self._styles,
            "table": body_tables,
            "legend": self._legend,
            "charset": charset,
        }


def main():
    diff_specs = collect_files(Path(FIN0), Path(FIN1))
    diff = MultiHtmlDiff().make_multi_file(diff_specs=diff_specs)
    with open("comparison_report.html", "w") as f:
        f.write(diff)


def collect_files(before_root: Path, after_root: Path) -> list[DiffSpec]:
    before_files = glob_path_no_parent(before_root, "*.svg")
    after_files = glob_path_no_parent(after_root, "*.svg")
    all_files = sorted(before_files | after_files)
    diff_specs = []

    for path in all_files:
        match (path in before_files, path in after_files):
            case (True, True):
                before = path_to_parsed(before_root, path)
                after = path_to_parsed(after_root, path)
                state = "unchanged" if before == after else "changed"
            case (True, False):
                before = path_to_parsed(before_root, path)
                after = []
                state = "remove"
            case (False, True):
                before = []
                after = path_to_parsed(before_root, path)
                state = "added"
            case (False, False):
                raise RuntimeError(f"{path} does not exist before or after.")

        diff_specs.append(DiffSpec(before=before, after=after, path=path, state=state))

    return diff_specs


def glob_path_no_parent(root: Path, glob: str, recurse_symlinks: bool = True):
    return set(
        rpath.relative_to(root)
        for rpath in root.rglob(glob, recurse_symlinks=recurse_symlinks)
    )


def path_to_parsed(root, path):
    return parse_node(ET.fromstring((root / path).read_text()), [])


def parse_node(
    node: Element,
    parsed: list[str],
    indent: str = "",
    depth: str = "@0",
) -> list[str]:
    # `depth` helps the diff algorthim not get confused when there are multiple tags of the same name in a row.
    parsed.append(f"{indent}<{no_name_space(node.tag)} {depth}>")

    parse_attributes(node, parsed, indent=indent)

    for index, child in enumerate(node.findall("*")):
        parse_node(
            child,
            parsed,
            indent=indent + INDENT,
            depth=depth + f"/{index}",
        )

    parsed.append(f"{indent}</{no_name_space(node.tag)} {depth}>")
    return parsed


def no_name_space(tag: str) -> str:
    _, _, only_tag = tag.rpartition("}")
    return only_tag


def parse_attributes(node: Element, parsed: list[str], indent: str):
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


def parse_d(indent: str, name: str, value: str) -> list[str]:
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    parts = re.split(r"([a-zA-Z]+)", value)
    parts = list(filter(None, parts))
    pairs = list(batched(parts, 2))
    pad = pad_min(pairs)
    for index, elem in enumerate(pairs):
        parsed.append(f"{indent}[{index:0{pad}d}] {elem[0]} {elem[1].strip()}")
    return parsed


def parse_points(indent: str, name: str, value: str) -> list[str]:
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    pairs = list(batched(value.split(), 2))
    pad = pad_min(pairs)
    for index, elem in enumerate(pairs):
        parsed.append(f"{indent}[{index:0{pad}d}] ({elem[0]}, {elem[1]})")
    return parsed


def parse_transform(indent: str, name: str, value: str) -> list[str]:
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    parts = split_transforms(value)
    for part in parts:
        parsed.append(f"{indent}{part}")
    return parsed


def split_transforms(transform_str: str) -> list[str]:
    # Match things like: translate(...), rotate(...), scale(...), etc.
    # - [a-zA-Z]+   → function name
    # - \([^)]*\)   → everything inside the parentheses
    pattern = r"[a-zA-Z]+\([^)]*\)"
    return re.findall(pattern, transform_str)


def parse_viewbox(indent: str, name: str, value: str) -> list[str]:
    parsed = [f"{indent}@{name}:"]
    indent += INDENT
    pad = pad_min(value.split())
    for index, elem in enumerate(value.split()):
        parsed.append(f"{indent}[{index:0{pad}d}] {elem}")
    return parsed


def parse_misc(indent: str, name: str, value: str) -> str:
    return f"{indent}@{name}: {value}"


def pad_min(seq: Sequence, min: int = 4):
    # in case the sequence is empty
    if len(seq) == 0:
        return min
    return max(min, math.ceil(math.log10(len(seq))))


if __name__ == "__main__":
    main()
