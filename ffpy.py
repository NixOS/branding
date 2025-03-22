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
        remove_bearing=True,
    ):
        self.font = fontforge.open(str(font_file))
        self.glyph = self.font[character]
        self._transform_glyph(scale, remove_bearing)

    def _transform_glyph(self, scale, remove_bearing):
        x_offset = 0
        if remove_bearing:
            x_offset = -self.glyph.left_side_bearing

        self.glyph.transform(
            (
                scale,
                0,
                0,
                -scale,
                x_offset,
                0,
            )
        )

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


class Characters:
    def __init__(
        self,
        characters: list[str],
        spacings: list[int],
    ):
        self.characters = [Character(elem) for elem in characters]
        x_offset = 0
        for character, spacing in zip(self.characters, spacings):
            x_offset += spacing
            character.glyph.transform((1, 0, 0, 1, x_offset, 0))
            character_width = (
                character.glyph.boundingBox()[2] - character.glyph.boundingBox()[0]
            )
            x_offset += character_width

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


my_char = Characters(
    characters=["N", "i", "x", "O", "S"],
    spacings=[200, 90, 70, 50, 10],
)
with open(Path("blah.svg"), "w") as file:
    file.write(str(my_char.make_svg()))
