from dataclasses import dataclass
from pathlib import Path

import fontforge
import svg


class Character:
    def __init__(
        self,
        character,
        # font_file=Path("./vegur.602/Vegur-Regular-0.602.otf"),
        # font_file=Path("./vegur_0701/Vegur-Regular.otf"),
        font_file=Path("./route159_110/Route159-Regular.otf"),
        scale=1,
        flip_x=False,
        flip_y=True,
        remove_bearing=True,
    ):
        self.font = fontforge.open(str(font_file))
        self.glyph = self.font[character]
        self._transform_glyph(scale, flip_x, flip_y, remove_bearing)

    def _transform_glyph(self, scale, flip_x, flip_y, remove_bearing):
        self.glyph.transform(
            (
                (-1 if flip_x else 1) * scale,
                0,
                0,
                (-1 if flip_y else 1) * scale,
                0,
                0,
            )
        )

        x_offset = 0
        if remove_bearing:
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

    def get_glyph_path(self):
        foreground = self.glyph.foreground
        path = []

        for contour in foreground:
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
        return svg.Path(d=self.get_glyph_path())

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


@dataclass
class Characters:
    characters: list[Character]
    spacings: list[int]

    def __post_init__(self):
        self._set_spacings()

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

    def make_svg(self):
        constants = {"size": 800, "scale": 1}

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=-constants["size"] * 0,
                min_y=-constants["size"] * 1,
                width=constants["size"] * 4,
                height=constants["size"] * 1,
            ),
            elements=[elem.get_svg_element() for elem in self.characters],
        )


@dataclass
class DimensionedCharacters(Characters):
    reference_size: int = 1024

    def __post_init__(self):
        super().__post_init__()
        # self._set_ref_size()

    def _set_ref_size(self):
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

    def make_dimensioned_svg(self):
        constants = {"size": self.reference_size * 1.1, "scale": 1}
        bbox = self.boundingBox

        return svg.SVG(
            viewBox=svg.ViewBoxSpec(
                min_x=-constants["size"] * 0,
                min_y=-constants["size"] * 1,
                width=constants["size"] * 4,
                height=constants["size"] * 1,
            ),
            elements=[
                svg.Rect(  # TODO: delete
                    x=0,
                    y=-constants["size"],
                    width=4 * constants["size"],
                    height=constants["size"],
                    fill="#8888ee",
                ),
            ]
            + [elem.get_svg_element() for elem in self.characters]
            + [
                svg.Rect(
                    x=bbox[0],
                    y=bbox[1],
                    width=bbox[2] - bbox[0],
                    height=bbox[3] - bbox[1],
                    stroke="black",
                    stroke_width=4,
                    stroke_dasharray=8,
                    fill="transparent",
                )
            ],
        )


# my_char = Characters(
#     characters=[
#         Character("N"),
#         Character("i", flip_x=True),
#         Character("x"),
#         Character("O"),
#         Character("S"),
#     ],
#     spacings=[200, 90, 70, 50, 10],
# )
# with open(Path("blah.svg"), "w") as file:
#     file.write(str(my_char.make_svg()))

my_char_dim = DimensionedCharacters(
    characters=[
        Character("N"),
        Character("i", flip_x=True),
        Character("x"),
        Character("O"),
        Character("S"),
    ],
    spacings=[200, 90, 70, 50, 10],
    # spacings=[0, 124, 96, 70, 14],
    # spacings=[0, 0, 0, 0, 0],
    reference_size=1024,
)
with open(Path("blah-dim.svg"), "w") as file:
    file.write(str(my_char_dim.make_dimensioned_svg()))
