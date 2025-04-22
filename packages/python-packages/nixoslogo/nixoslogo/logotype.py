import os
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fontforge
import svg

from .colors import NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE
from .geometry import Point
from .annotations import ConstructionLines, DimensionLines

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


@dataclass(kw_only=True)
class FontLoader:
    font_file: Path = Path(os.getenv("NIXOS_LOGOTYPE_FONT_FILE"))
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


@dataclass
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
    def boundingBox(self):
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
        return self.boundingBox[0]

    @property
    def yMin(self):
        return self.boundingBox[1]

    @property
    def xMax(self):
        return self.boundingBox[2]

    @property
    def yMax(self):
        return self.boundingBox[3]

    @property
    def width(self):
        return self.boundingBox[2] - self.boundingBox[0]

    @property
    def height(self):
        return self.boundingBox[3] - self.boundingBox[1]

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


@dataclass
class DimensionedLogotype(Logotype):
    construction_lines: ConstructionLines
    dimension_lines: DimensionLines

    def __post_init__(self):
        super().__post_init__()

    def make_dimensioned_svg(self):
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
                []
                + self.svg_bounding_box()
                + self.dimension_cap_height()
                + self.dimension_spacings()
                + [elem.get_svg_element() for elem in self.characters],
            ),
        )

    def svg_bounding_box(self):
        bbox = self.boundingBox

        return [
            svg.Rect(
                x=bbox[0],
                y=bbox[1],
                width=self.width,
                height=self.height,
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill="transparent",
            ),
            self.dimension_lines.make_dimension_line(
                point1=Point((self.xMax, self.yMin)),
                point2=Point((self.xMin, self.yMin)),
                flip=False,
                side="right",
                offset=1 / 16,
                reference=self.capHeight,
                fractional=False,
            ),
            self.dimension_lines.make_dimension_line(
                point1=Point((self.xMax, self.yMax)),
                point2=Point((self.xMax, self.yMin)),
                flip=False,
                side="right",
                offset=1 / 4,
                reference=self.capHeight,
                fractional=False,
            ),
        ]

    def dimension_cap_height(self):
        point1 = Point((self.characters[0].xMin, self.characters[0].yMin))
        point2 = Point((self.characters[0].xMin, self.characters[0].yMax))
        return [
            self.dimension_lines.make_dimension_line(
                point1=point1,
                point2=point2,
                flip=False,
                side="right",
                offset=1 / 4,
                reference=self.capHeight,
            )
        ]

    def dimension_spacings(self):
        points = [
            (
                Point((self.characters[index + 0].xMax, self.yMin)),
                Point((self.characters[index + 1].xMin, self.yMin)),
            )
            for index in range(4)
        ]
        offsets = [
            self.capHeight / (point1 - point2).length() for point1, point2 in points
        ]
        sides = ["left", "right", "right", "right"]
        return [
            self.dimension_lines.make_dimension_line(
                point1=point1,
                point2=point2,
                flip=False,
                side=side,
                offset=offset,
                reference=self.capHeight,
                text_offset=True,
                fractional=False,
            )
            for (point1, point2), offset, side in zip(points, offsets, sides)
        ]
