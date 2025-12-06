import math
import re
import xml.etree.ElementTree as ET
from itertools import batched
from pathlib import Path
from xml.etree.ElementTree import Element

INDENT = 2
FIN = "./result-unrounded/media-kit/nixos-logo-default-gradient-black-regular-horizontal-recommended.svg"


def main():
    with open(Path(FIN), "r") as file_in:
        root = ET.fromstring(file_in.read())
    parsed = parse_node(root, [])
    print("\n".join(parsed))


def parse_node(node: Element, parsed: list[str], indent: str = "") -> list[str]:
    parsed.append(f"{indent}<{no_name_space(node.tag)}>")

    parse_attributes(node, parsed, indent=indent)

    for child in node.findall("*"):
        parse_node(child, parsed, indent=indent + " " * INDENT)

    parsed.append(f"{indent}</{no_name_space(node.tag)}>")
    return parsed


def no_name_space(tag: str) -> str:
    _, _, only_tag = tag.rpartition("}")
    return only_tag


def parse_attributes(node: Element, parsed: list[str], indent: str):
    indent += " " * INDENT
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
    indent += " " * INDENT
    parts = re.split(r"([a-zA-Z]+)", value)
    parts = list(filter(None, parts))
    pairs = list(batched(parts, 2))
    for elem in pairs:
        parsed.append(f"{indent}{elem[0]} {elem[1].strip()}")
    return parsed


def parse_points(indent: str, name: str, value: str) -> list[str]:
    parsed = [f"{indent}@{name}:"]
    indent += " " * INDENT
    pairs = list(batched(value.split(), 2))
    pad = math.ceil(math.log10(len(pairs)))
    for index, elem in enumerate(pairs):
        parsed.append(f"{indent}[{index:0{pad}d}] ({elem[0]}, {elem[1]})")
    return parsed


def parse_transform(indent: str, name: str, value: str) -> list[str]:
    parsed = [f"{indent}@{name}:"]
    indent += " " * INDENT
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
    indent += " " * INDENT
    pad = math.ceil(math.log10(len(value.split())))
    for index, elem in enumerate(value.split()):
        parsed.append(f"{indent}[{index:0{pad}d}] {elem}")
    return parsed


def parse_misc(indent: str, name: str, value: str) -> str:
    return f"{indent}@{name}: {value}"


if __name__ == "__main__":
    main()
