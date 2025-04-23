import string
from abc import ABC, abstractmethod
from enum import Enum, auto

import svg

from nixoslogo.colors import Color
from nixoslogo.layout import Canvas

# === Enums ===


class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()


class ColorStyle(Enum):
    FLAT = auto()
    GRADIENT = auto()


# === Constants ===


DEFAULT_CHARACTER_TRANSFORMS = {
    "scale_x": 1,
    "scale_y": -1,
    "remove_bearing": True,
}
DEFAULT_FONT_TRANSFORMS = {
    char: DEFAULT_CHARACTER_TRANSFORMS for char in string.ascii_letters
} | {"i": DEFAULT_CHARACTER_TRANSFORMS | {"scale_x": -1}}

DEFAULT_LOGOTYPE_SPACINGS = (0, 90, 70, 50, 10)
DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING = (200,) + DEFAULT_LOGOTYPE_SPACINGS[1:]

NIXOS_DARK_BLUE = Color("oklch", (0.5774, 0.1248, 264))
NIXOS_LIGHT_BLUE = Color("oklch", (0.7636, 0.0866, 240))
RAINBOW_COLORS = (
    Color("oklch", (0.51, 0.208963, 29.2339)),
    Color("oklch", (0.70, 0.204259, 43.491)),
    Color("oklch", (0.81, 0.168100, 76.78)),
    Color("oklch", (0.60, 0.175100, 147.56)),
    Color("oklch", (0.60, 0.141400, 241.38)),
    Color("oklch", (0.46, 0.194300, 288.71)),
)


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
