from dataclasses import dataclass
from pathlib import Path

import fontforge
import svg

from everything import (
    NIXOS_DARK_BLUE,
    NIXOS_LIGHT_BLUE,
    DimensionLines,
    LineGroup,
    Point,
)


@dataclass(kw_only=True)
class Character:
    character: str | None
    font_file: Path = Path("./route159_110/Route159-Regular.otf")
    color: str = "black"
    scale: float = 1
    flip_x: bool = False
    flip_y: bool = True
    remove_bearing: bool = True

    def __post_init__(self):
        self.font = fontforge.open(str(self.font_file))
        self.glyph = self.font[self.character]
        self._transform_glyph()

    def _transform_glyph(self):
        self.glyph.transform(
            (
                (-1 if self.flip_x else 1) * self.scale,
                0,
                0,
                (-1 if self.flip_y else 1) * self.scale,
                0,
                0,
            )
        )

        x_offset = 0
        if self.remove_bearing:
            x_offset = -self.glyph.left_side_bearing

        self.glyph.transform(
            (
                1,
                0,
                0,
                1,
                x_offset,
                0,
            )
        )

    @property
    def glyph_width(self):
        bbox = self.glyph.boundingBox()
        return bbox[2] - bbox[0]

    @property
    def glyph_height(self):
        bbox = self.glyph.boundingBox()
        return bbox[3] - bbox[1]

    @property
    def xMin(self):
        return self.glyph.boundingBox()[0]

    @property
    def yMin(self):
        return self.glyph.boundingBox()[1]

    @property
    def xMax(self):
        return self.glyph.boundingBox()[2]

    @property
    def yMax(self):
        return self.glyph.boundingBox()[3]

    def get_glyph_path(self, layer):
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
            d=self.get_glyph_path(self.glyph.foreground),
            fill=self.color,
        )

    def make_svg(self):
        constants = {"size": 800, "scale": 1}

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=-constants["size"],
                min_y=-constants["size"],
                width=constants["size"] * 2,
                height=constants["size"] * 2,
            ),
            elements=[
                svg.Rect(  # TODO: delete
                    x=0,
                    y=-constants["size"],
                    width=constants["size"],
                    height=constants["size"],
                    fill="#8888ee",
                ),
                self.get_svg_element(),
            ],
        )


@dataclass(kw_only=True)
class ModifiedCharacter(Character):
    character: str = "x"

    def __post_init__(self):
        super().__post_init__()

    def get_svg_element(self):
        foreground = self.glyph.foreground
        layer = [foreground[0][:2] + foreground[0][10:]]
        alt_layer = [foreground[0][2:10]]
        return [
            svg.Path(
                d=self.get_glyph_path(layer),
                fill=NIXOS_LIGHT_BLUE.to_string(),
            ),
            svg.Path(
                d=self.get_glyph_path(alt_layer),
                fill=NIXOS_DARK_BLUE.to_string(),
            ),
        ]


@dataclass
class Characters:
    characters: list[Character]
    spacings: list[int]
    reference_size: int | None

    def __post_init__(self):
        self._set_ref_size()
        self._set_spacings()

    def _set_ref_size(self):
        if self.reference_size is None:
            self.reference_size = int(self.characters[0].font.capHeight)

        for character in self.characters:
            character.glyph.transform(
                (
                    self.reference_size / character.font.capHeight,
                    0,
                    0,
                    self.reference_size / character.font.capHeight,
                    0,
                    0,
                )
            )

    def _set_spacings(self):
        x_offset = 0
        for character, spacing in zip(self.characters, self.spacings):
            x_offset += spacing
            character.glyph.transform((1, 0, 0, 1, x_offset, 0))
            character_width = (
                character.glyph.boundingBox()[2] - character.glyph.boundingBox()[0]
            )
            x_offset += character_width

    @property
    def boundingBox(self):
        return [
            f(elem)
            for f, elem in zip(
                (min, min, max, max),
                list(zip(*(elem.glyph.boundingBox() for elem in self.characters))),
            )
        ]

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

    def make_svg(self):
        viewport = (
            self.xMin - self.reference_size / 2,
            self.yMin - self.reference_size / 2,
            self.width + self.reference_size,
            self.height + self.reference_size,
        )

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=viewport[0],
                min_y=viewport[1],
                width=viewport[2],
                height=viewport[3],
            ),
            elements=[
                # svg.Rect(  # TODO: delete
                #     x=viewport[0],
                #     y=viewport[1],
                #     width=viewport[2],
                #     height=viewport[3],
                #     fill="#8888ee",
                # ),
            ]
            + [elem.get_svg_element() for elem in self.characters],
        )


@dataclass
class DimensionedCharacters(Characters, DimensionLines):
    construction_lines: LineGroup
    dimension_lines: LineGroup

    def __post_init__(self):
        super().__post_init__()

    def make_dimensioned_svg(self):
        viewport = (
            self.xMin - self.reference_size / 2,
            self.yMin - self.reference_size / 2,
            self.width + self.reference_size,
            self.height + self.reference_size,
        )

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=viewport[0],
                min_y=viewport[1],
                width=viewport[2],
                height=viewport[3],
            ),
            elements=[
                # svg.Rect(  # TODO: delete
                #     x=viewport[0],
                #     y=viewport[1],
                #     width=viewport[2],
                #     height=viewport[3],
                #     fill="#8888ee",
                # ),
            ]
            + self.svg_bounding_box()
            + self.dimension_cap_height()
            + self.dimension_spacings()
            + [elem.get_svg_element() for elem in self.characters],
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
            self.make_dimension_line(
                point1=Point((self.xMax, self.yMin)),
                point2=Point((self.xMin, self.yMin)),
                flip=False,
                side="right",
                offset=1 / 16,
                reference=self.reference_size,
                fractional=False,
            ),
            self.make_dimension_line(
                point1=Point((self.xMax, self.yMax)),
                point2=Point((self.xMax, self.yMin)),
                flip=False,
                side="right",
                offset=1 / 4,
                reference=self.reference_size,
                fractional=False,
            ),
        ]

    def dimension_cap_height(self):
        point1 = Point((self.characters[0].xMin, self.characters[0].yMin))
        point2 = Point((self.characters[0].xMin, self.characters[0].yMax))
        return [
            self.make_dimension_line(
                point1=point1,
                point2=point2,
                flip=False,
                side="right",
                offset=1 / 4,
                reference=self.reference_size,
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
            self.reference_size / (point1 - point2).length()
            for point1, point2 in points
        ]
        sides = ["left", "right", "right", "right"]
        return [
            self.make_dimension_line(
                point1=point1,
                point2=point2,
                flip=False,
                side=side,
                offset=offset,
                reference=self.reference_size,
                text_offset=True,
                fractional=False,
            )
            for (point1, point2), offset, side in zip(points, offsets, sides)
        ]


def make_logotype():
    my_char = Characters(
        characters=[
            Character(character="N"),
            Character(character="i", flip_x=True),
            Character(character="x"),
            Character(character="O"),
            Character(character="S"),
        ],
        spacings=[200, 90, 70, 50, 10],
        reference_size=None,
    )
    with open(Path("logotype.svg"), "w") as file:
        file.write(str(my_char.make_svg()))

    # close out font because it retains state
    my_char.characters[0].font.close()


def make_modified_logotype():
    my_char = Characters(
        characters=[
            Character(character="N"),
            Character(character="i", flip_x=True),
            ModifiedCharacter(),
            Character(character="O"),
            Character(character="S"),
        ],
        spacings=[200, 90, 70, 50, 10],
        reference_size=None,
    )
    with open(Path("logotype-modified.svg"), "w") as file:
        file.write(str(my_char.make_svg()))

    # close out font because it retains state
    my_char.characters[0].font.close()


def make_dimensioned_logotype():
    construction_lines = LineGroup(
        name="construction",
        stroke="black",
        stroke_width=2,
        stroke_dasharray=16,
        font_size="2rem",
    )
    dimension_lines = LineGroup(
        name="dimension",
        stroke="red",
        stroke_width=1,
        stroke_dasharray=8,
        font_size="2rem",
    )
    my_char_dim = DimensionedCharacters(
        characters=[
            Character(character="N"),
            Character(character="i", flip_x=True),
            Character(character="x"),
            Character(character="O"),
            Character(character="S"),
        ],
        spacings=[0, 90, 70, 50, 10],
        reference_size=None,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
    )
    with open(Path("logotype-dimensioned.svg"), "w") as file:
        file.write(str(my_char_dim.make_dimensioned_svg()))

    # close out font because it retains state
    my_char_dim.characters[0].font.close()


make_logotype()
make_modified_logotype()
make_dimensioned_logotype()
