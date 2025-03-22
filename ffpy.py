from pathlib import Path

import fontforge
import svg


class Character:
    def __init__(
        self,
        character,
        font_file=Path("./vegur.602/Vegur-Regular-0.602.otf"),
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


my_char = Character("N")
with open(Path("blah.svg"), "w") as file:
    file.write(str(my_char.make_svg()))
