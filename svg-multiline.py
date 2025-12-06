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
    parse_node(root)


def parse_node(node: Element, indent: str = ""):
    print(f"{indent}<{no_name_space(node.tag)}>")

    parse_attributes(node, indent=indent)

    for child in node.findall("*"):
        parse_node(child, indent=indent + " " * INDENT)

    print(f"{indent}</{no_name_space(node.tag)}>")


def no_name_space(tag: str) -> str:
    _, _, only_tag = tag.rpartition("}")
    return only_tag


def parse_attributes(node: Element, indent: str):
    indent += " " * INDENT
    for name, value in node.attrib.items():
        match name:
            case "d":
                parse_d(indent, name, value)
            case "points":
                parse_points(indent, name, value)
            case "transform":
                parse_transform(indent, name, value)
            case "viewBox":
                parse_viewbox(indent, name, value)
            case _:
                parse_misc(indent, name, value)


def parse_d(indent: str, name: str, value: str):
    print(f"{indent}@{name}:")
    indent += " " * INDENT
    parts = re.split(r"([a-zA-Z]+)", value)
    parts = list(filter(None, parts))
    pairs = list(batched(parts, 2))
    for elem in pairs:
        print(f"{indent}{elem[0]} {elem[1].strip()}")


def parse_points(indent: str, name: str, value: str):
    print(f"{indent}@{name}:")
    indent += " " * INDENT
    pairs = list(batched(value.split(), 2))
    pad = math.ceil(math.log10(len(pairs)))
    for index, elem in enumerate(pairs):
        print(f"{indent}[{index:0{pad}d}] ({elem[0]}, {elem[1]})")


def parse_transform(indent: str, name: str, value: str):
    print(f"{indent}@{name}:")
    indent += " " * INDENT
    parts = split_transforms(value)
    for part in parts:
        print(f"{indent}{part}")


def split_transforms(transform_str: str) -> list[str]:
    # Match things like: translate(...), rotate(...), scale(...), etc.
    # - [a-zA-Z]+   → function name
    # - \([^)]*\)   → everything inside the parentheses
    pattern = r"[a-zA-Z]+\([^)]*\)"
    return re.findall(pattern, transform_str)


def parse_viewbox(indent: str, name: str, value: str):
    print(f"{indent}@{name}:")
    indent += " " * INDENT
    pad = math.ceil(math.log10(len(value.split())))
    for index, elem in enumerate(value.split()):
        print(f"{indent}[{index:0{pad}d}] {elem}")


def parse_misc(indent: str, name: str, value: str):
    print(f"{indent}@{name}: {value}")


if __name__ == "__main__":
    main()
