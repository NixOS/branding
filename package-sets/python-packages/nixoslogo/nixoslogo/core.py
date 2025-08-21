import os
import string
from abc import ABC, abstractmethod
from enum import Enum, auto
from functools import partial
from pathlib import Path

import svg
import tomllib
from lxml import etree

from nixoslogo.colors import Color
from nixoslogo.layout import Canvas

# === Functions ===


def get_path_from_envvar(envvar) -> Path:
    path = os.getenv(envvar)
    if not path:
        raise EnvironmentError(
            f"{envvar} is not set. "
            "Please provide a font path explicitly or set the environment variable."
        )
    return Path(path)


def get_color_by_name(palette, name):
    return list(filter(lambda color: color["name"] == name, palette))[0]


get_nixos_logotype_font_file = partial(
    get_path_from_envvar,
    "NIXOS_LOGOTYPE_FONT_FILE",
)

get_nixos_annotation_font_file = partial(
    get_path_from_envvar,
    "NIXOS_ANNOTATIONS_FONT_FILE",
)

get_nixos_color_palette_file = partial(
    get_path_from_envvar,
    "NIXOS_COLOR_PALETTE_FILE",
)

# === Constants ===


CHARACTER_GLYPHNAME_MAP = {
    " ": "space",
    "%": "percent",
    ".": "period",
    "/": "slash",
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    # "_": "underscore",
}

DEFAULT_CHARACTER_TRANSFORMS = {
    "scale_x": 1,
    "scale_y": -1,
}
DEFAULT_CHARACTER_SET = list(string.ascii_letters) + list(
    CHARACTER_GLYPHNAME_MAP.values()
)

DEFAULT_ROUTE159_TRANSFORMS = {
    char: DEFAULT_CHARACTER_TRANSFORMS for char in DEFAULT_CHARACTER_SET
} | {"i": DEFAULT_CHARACTER_TRANSFORMS | {"scale_x": -1}}
DEFAULT_JURA_TRANSFORMS = {
    char: DEFAULT_CHARACTER_TRANSFORMS for char in DEFAULT_CHARACTER_SET
}

DEFAULT_LOGOTYPE_SPACINGS = (0, 90, 70, 50, 10)
DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING = (200,) + DEFAULT_LOGOTYPE_SPACINGS[1:]


with open(get_nixos_color_palette_file(), "rb") as f:
    NIXOS_COLOR_PALETTE = tomllib.load(f)

PALETTE_DEFAULT_COLORS = NIXOS_COLOR_PALETTE["logos"]["default"]
PALETTE_RAINBOW_COLORS = NIXOS_COLOR_PALETTE["logos"]["rainbow"]
PALETTE_TRANS_COLORS = NIXOS_COLOR_PALETTE["logos"]["trans"]
PALETTE_PRIMARY_COLORS = NIXOS_COLOR_PALETTE["palette"]["primary"]
PALETTE_SECONDARY_COLORS = NIXOS_COLOR_PALETTE["palette"]["secondary"]
PALETTE_ACCENT_COLORS = NIXOS_COLOR_PALETTE["palette"]["accent"]

NIXOS_DARK_BLUE = Color(
    "oklch",
    get_color_by_name(PALETTE_DEFAULT_COLORS, "NixOS Dark Blue")["value"],
)
NIXOS_LIGHT_BLUE = Color(
    "oklch",
    get_color_by_name(PALETTE_DEFAULT_COLORS, "NixOS Light Blue")["value"],
)
RAINBOW_COLORS = tuple(
    map(
        lambda color: Color("oklch", color["value"]),
        PALETTE_RAINBOW_COLORS,
    )
)
TRANS_COLORS = tuple(
    map(
        lambda color: Color("oklch", color["value"]),
        PALETTE_TRANS_COLORS,
    )
)

NIXOS_BLACK = Color(
    "oklch",
    get_color_by_name(PALETTE_PRIMARY_COLORS, "Black")["value"],
)

NIXOS_WHITE = Color(
    "oklch",
    get_color_by_name(PALETTE_PRIMARY_COLORS, "White")["value"],
)


# === Enums ===


class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()


class ColorStyle(Enum):
    FLAT = auto()
    GRADIENT = auto()


class LogoLayout(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


class LogomarkColors(Enum):
    DEFAULT = (NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE)
    RAINBOW = RAINBOW_COLORS
    TRANS = TRANS_COLORS
    BLACK = (NIXOS_BLACK,)
    WHITE = (NIXOS_WHITE,)


class LogotypeStyle(Enum):
    REGULAR = auto()
    LAMBDAPRIME = auto()


# === Base Classes ===


class BaseRenderable(ABC):
    def __init__(
        self,
        canvas: Canvas | None = None,
        background_color: str | None = None,
        **kwargs,
    ):
        self.canvas = canvas
        self.background_color = background_color
        self._init_canvas()

    @property
    @abstractmethod
    def elements_bounding_box(self) -> tuple[float, float, float, float]: ...

    @abstractmethod
    def _get_clearspace(self) -> float: ...

    @abstractmethod
    def make_svg_elements(self): ...

    @abstractmethod
    def make_filename(self, extras: tuple[str]) -> str: ...

    def _init_canvas(self):
        if self.canvas is None:
            min_x, min_y, max_x, max_y = self.elements_bounding_box
            clear_space = self._get_clearspace()

            min_x -= clear_space
            min_y -= clear_space
            max_x += clear_space
            max_y += clear_space

            self.canvas = Canvas(
                min_x=min_x,
                min_y=min_y,
                width=max_x - min_x,
                height=max_y - min_y,
            )

    @property
    def canvas_bounding_box(self):
        return (
            self.canvas.min_x,
            self.canvas.min_y,
            self.canvas.min_x + self.canvas.width,
            self.canvas.min_y + self.canvas.height,
        )

    def make_svg_background(self):
        return (
            ()
            if self.background_color is None
            else self.canvas.make_svg_background(fill=self.background_color)
        )

    def make_svg(self):
        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=self.make_svg_background() + self.make_svg_elements(),
        )

    def write_svg(self, filename=None):
        if filename is None:
            filename = self.make_filename()
        filename = filename.replace("/", "_")
        with open(Path(filename + ".svg"), "w", encoding="utf-8") as file:
            etree.canonicalize(str(self.make_svg()), out=file)

    @property
    def elements_x_min(self):
        return self.elements_bounding_box[0]

    @property
    def elements_y_min(self):
        return self.elements_bounding_box[1]

    @property
    def elements_x_max(self):
        return self.elements_bounding_box[2]

    @property
    def elements_y_max(self):
        return self.elements_bounding_box[3]

    @property
    def elements_width(self):
        return self.elements_x_max - self.elements_x_min

    @property
    def elements_height(self):
        return self.elements_y_max - self.elements_y_min
