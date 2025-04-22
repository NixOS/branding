import os
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fontforge
import svg

from .colors import NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE

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


def _default_font_file() -> Path:
    path = os.getenv("NIXOS_LOGOTYPE_FONT_FILE")
    if not path:
        raise EnvironmentError(
            "NIXOS_LOGOTYPE_FONT_FILE is not set. "
            "Please provide a font path explicitly or set the environment variable."
        )
    return Path(path)


@dataclass(kw_only=True)
class FontLoader:
    font_file: Path = field(default_factory=_default_font_file)
    transforms_map: dict[str, Any] = field(
        default_factory=lambda: DEFAULT_FONT_TRANSFORMS
    )
    capHeight: int | None = None

    def __post_init__(self):
        self.font = fontforge.open(str(self.font_file))
        self._set_ref_size()

        for character, transforms in self.transforms_map.items():
            self._scale_glyph(character, transforms)
            self._offset_glyph(character, transforms)

    def _set_ref_size(self):
        """
        Conditionally update the font size.

        The glyphs can be scaled by updating the `em` attribute.
        `capHeight` goes to zero because we are flipping glyphs so that is stored off for later use.
        """
        if self.capHeight is None:
            self.scale = 1
            self.capHeight = int(self.font.capHeight)
        else:
            self.scale = self.capHeight / self.font.capHeight
            self.font.em = round(self.font.em * self.scale)

    def _scale_glyph(self, character, transforms):
        """Scale a glyph; primarily used for vertically flipping."""
        self.font[character].transform(
            (
                transforms["scale_x"],
                0,
                0,
                transforms["scale_y"],
                0,
                0,
            )
        )

    def _offset_glyph(self, character, transforms):
        """Offset a glyph; primarily used to remove the left side bearing."""
        x_offset = 0
        if transforms["remove_bearing"]:
            x_offset = -self.font[character].left_side_bearing

        self.font[character].transform(
            (
                1,
                0,
                0,
                1,
                x_offset,
                0,
            )
        )


def make_view_box(viewport):
    return svg.ViewBoxSpec(
        min_x=viewport[0],
        min_y=viewport[1],
        width=viewport[2],
        height=viewport[3],
    )


def make_svg_background(viewport, color="#8888ee"):  # TODO: delete
    return [
        svg.Rect(
            x=viewport[0],
            y=viewport[1],
            width=viewport[2],
            height=viewport[3],
            fill=color,
        ),
    ]


@dataclass(kw_only=True)
class Character:
    character: str | None
    loader: FontLoader
    color: str = "black"

    def __post_init__(self):
        self.font = self.loader.font
        self.glyph = self.font[self.character]
        self.layer = self.glyph.foreground.dup()

    @property
    def width(self):
        bbox = self.layer.boundingBox()
        return bbox[2] - bbox[0]

    @property
    def height(self):
        bbox = self.layer.boundingBox()
        return bbox[3] - bbox[1]

    @property
    def xMin(self):
        return self.layer.boundingBox()[0]

    @property
    def yMin(self):
        return self.layer.boundingBox()[1]

    @property
    def xMax(self):
        return self.layer.boundingBox()[2]

    @property
    def yMax(self):
        return self.layer.boundingBox()[3]

    def get_path(self, layer):
        path = []
        for contour in layer:
            first_iteration = True
            points = list(contour)

            # If last point is a control point
            if not points[-1].on_curve:
                points.append(points[0])

            while points:
                # First iteration of a contour should always be a move.
                if first_iteration:
                    point = points.pop(0)
                    element = svg.MoveTo(point.x, point.y)
                    path.append(element)
                    first_iteration = False
                    continue

                if points[0].on_curve:
                    # If the next point is on curve, it is a straight line from the previous point.
                    point = points.pop(0)
                    element = svg.LineTo(point.x, point.y)
                    path.append(element)
                    continue
                else:
                    # If the next point is off curve, it is a control point and so the next 3 points make a Bézier curve.
                    # lol
                    points_bezier = [
                        elem
                        for pair in (
                            (point.x, point.y)
                            for point in (points.pop(0) for _ in range(3))
                        )
                        for elem in pair
                    ]
                    element = svg.CubicBezier(*points_bezier)
                    path.append(element)

        return path

    def get_svg_element(self):
        return svg.Path(
            d=self.get_path(self.layer),
            fill=self.color,
        )

    def make_svg(self):
        viewport = (
            self.xMin - self.width / 2,
            self.yMin - self.height / 2,
            self.width * 2,
            self.height * 2,
        )

        return svg.SVG(
            viewBox=make_view_box(viewport),
            elements=(
                make_svg_background(viewport)
                + [
                    self.get_svg_element(),
                ]
            ),
        )


@dataclass(kw_only=True)
class ModifiedCharacterX(Character):
    character: str = "x"

    def __post_init__(self):
        super().__post_init__()

    def get_svg_element(self):
        upper = [self.layer[0][:2] + self.layer[0][10:]]
        lower = [self.layer[0][2:10]]
        return [
            svg.Path(
                d=self.get_path(upper),
                fill=NIXOS_LIGHT_BLUE.to_string(),
            ),
            svg.Path(
                d=self.get_path(lower),
                fill=NIXOS_DARK_BLUE.to_string(),
            ),
        ]


@dataclass(kw_only=True)
class Logotype:
    characters: list[Character]
    spacings: tuple[int]

    def __post_init__(self):
        self.capHeight = self.characters[0].loader.capHeight
        self.scale = self.characters[0].loader.scale
        self._set_spacings()

    def _set_spacings(self):
        x_offset = 0
        for character, spacing in zip(self.characters, self.spacings):
            x_offset += spacing * self.scale
            character.layer.transform((1, 0, 0, 1, x_offset, 0))
            character_width = (
                character.layer.boundingBox()[2] - character.layer.boundingBox()[0]
            )
            x_offset += character_width

    @property
    def elements_bounding_box(self):
        characters_box = [
            f(elem)
            for f, elem in zip(
                (min, min, max, max),
                list(zip(*(elem.layer.boundingBox() for elem in self.characters))),
            )
        ]
        with_lead_spacing = [characters_box[0] - self.spacings[0]] + characters_box[1:]
        return with_lead_spacing

    @property
    def xMin(self):
        return self.elements_bounding_box[0]

    @property
    def yMin(self):
        return self.elements_bounding_box[1]

    @property
    def xMax(self):
        return self.elements_bounding_box[2]

    @property
    def yMax(self):
        return self.elements_bounding_box[3]

    @property
    def width(self):
        return self.elements_bounding_box[2] - self.elements_bounding_box[0]

    @property
    def height(self):
        return self.elements_bounding_box[3] - self.elements_bounding_box[1]

    def make_svg_elements(self):
        return tuple(elem.get_svg_element() for elem in self.characters)

    def make_svg(self):
        viewport = (
            self.xMin - self.capHeight / 2,
            self.yMin - self.capHeight / 2,
            self.width + self.capHeight,
            self.height + self.capHeight,
        )

        return svg.SVG(
            viewBox=make_view_box(viewport),
            elements=(
                # make_svg_background(viewport)
                [] + [elem.get_svg_element() for elem in self.characters]
            ),
        )
