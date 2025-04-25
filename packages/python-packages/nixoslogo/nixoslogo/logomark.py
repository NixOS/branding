import itertools
import math

import svg
from svg._types import Number

from nixoslogo.colors import Color
from nixoslogo.core import (
    NIXOS_DARK_BLUE,
    NIXOS_LIGHT_BLUE,
    BaseRenderable,
    ClearSpace,
    ColorStyle,
)
from nixoslogo.geometry import Point, Points, Vector, cosd, sind


class Lambda(BaseRenderable):
    def __init__(
        self,
        radius: int = 512,
        thickness: float = 1 / 4,
        gap: float = 1 / 32,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        **kwargs,
    ):
        self.radius = radius
        self.thickness = thickness
        self.gap = gap
        self.clear_space = clear_space
        super().__init__(**kwargs)

    @property
    def elements_bounding_box(self):
        double_up = [
            (
                point.x,
                point.y,
            )
            * 2
            for point in self.make_lambda_points()
        ]
        return tuple(
            predicate(elem)
            for predicate, elem in zip(
                (min, min, max, max),
                list(zip(*double_up)),
            )
        )

    def _get_clearspace(self):
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.elements_y_max / 2
            case ClearSpace.RECOMMENDED:
                return self.elements_y_max
            case _:
                raise Exception("Unknown ClearSpace")

    def make_svg_elements(self):
        pass

    def make_hexagon_points(self, radius: Number) -> Points:
        angles = [math.radians(angle) for angle in range(0, 360, 60)]
        return Points(
            [
                Point(
                    (
                        radius * math.cos(angle),
                        radius * math.sin(angle),
                    )
                )
                for angle in angles
            ]
        )

    # TODO - @djacu move to dimensioned.py and have DimensionedLogomark use DimensionedLambda
    def make_diagonal_line(self, radius: Number) -> list[Number]:
        hexagon_points = self.make_hexagon_points(radius)
        return Points([hexagon_points[1], hexagon_points[4]])

    # TODO - @djacu make another function that creates a dict of all the points
    # so they can be referenced by name. Then use dict values to make the Points list
    def make_lambda_points(
        self,
        radius: Number | None = None,
        thickness: Number | None = None,
        gap: Number | None = None,
    ) -> Points:
        radius = radius if radius is not None else self.radius
        thickness = thickness if thickness is not None else self.thickness
        gap = gap if gap is not None else self.gap

        hexagon_points = self.make_hexagon_points(radius)
        hex_top_left = hexagon_points[2]
        hex_bottom_left = hexagon_points[4]
        hex_bottom_right = hexagon_points[5]

        vector_0 = radius * thickness * Vector((cosd(0), sind(0)))
        vector_60 = radius * thickness * Vector((cosd(60), sind(60)))
        vector_270 = radius * thickness * Vector((cosd(270), sind(270)))
        vector_300 = radius * thickness * Vector((cosd(300), sind(300)))
        gap_vector = 2 * radius * gap * Vector((cosd(300), sind(300)))

        points = [
            (hex_top_left - vector_60 + gap_vector),
            (hex_top_left + vector_60 + gap_vector),
            (hex_bottom_right + vector_0),
            (hex_bottom_right - vector_0),
            (math.sqrt(3) * vector_270).to_point(),
            (hex_bottom_left + vector_0),
            hex_bottom_left,
            (hex_bottom_left - vector_300),
            (-vector_0).to_point(),
        ]

        # Need to negate the y-axis so the lambda is not upside down
        points = Points([Point((point.x, -point.y)) for point in points])
        return points

    # TODO - @djacu move to dimensioned.py and have DimensionedLogomark use DimensionedLambda
    def make_lambda_polygons(self):
        lambda_points_no_gap = self.make_lambda_points(gap=0)
        lambda_points_gap = self.make_lambda_points()
        return (
            svg.Polygon(
                points=lambda_points_no_gap.to_list(),
                stroke=self.object_lines.stroke,
                stroke_width=self.object_lines.stroke_width,
                fill=self.object_lines.fill,
                stroke_dasharray=4,
            ),
            svg.Polygon(
                points=lambda_points_gap.to_list(),
                stroke=self.object_lines.stroke,
                stroke_width=self.object_lines.stroke_width,
                fill=self.object_lines.fill,
            ),
        )


class Logomark(BaseRenderable):
    def __init__(
        self,
        ilambda: Lambda,  # TODO - @djacu see if you can set a default value of Lambda()
        color_style: ColorStyle,  # TODO - @djacu think about a default value
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        colors: tuple[Color] = (NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE),
        **kwargs,
    ):
        self.ilambda = ilambda
        self.colors = colors
        self.color_style = color_style
        self.clear_space = clear_space

        self._make_color_names()

        self._gradient_stop_offsets = [0, 25, 100]

        super().__init__(**kwargs)

    @property
    def elements_bounding_box(self):
        return (
            -self.circumradius,
            -self.inradius,
            self.circumradius,
            self.inradius,
        )

    @property
    def circumradius(self):
        """The logomark circumradius."""
        return max(point.x for points in self.make_flake_points() for point in points)

    @property
    def inradius(self):
        """The logomark inradius."""
        return self.circumradius * math.sqrt(3) / 2

    @property
    def snowflake_lambda_ratio(self):
        """The ratio between the snowflake and lambda radius."""
        return self.circumradius / self.ilambda.radius

    def _get_clearspace(self):
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.elements_y_max / 2
            case ClearSpace.RECOMMENDED:
                return self.elements_y_max
            case _:
                raise Exception("Unknown ClearSpace")

    def _make_color_names(self):
        match self.color_style:
            case ColorStyle.FLAT:
                self.color_names = tuple(color.to_string() for color in self.colors)
            case ColorStyle.GRADIENT:
                self.color_names = tuple(
                    color.gradient_color_name() for color in self.colors
                )
            case _:
                raise Exception("Unknown ColorStyle")

    def make_svg_elements(self):
        match self.color_style:
            case ColorStyle.FLAT:
                return self.make_clean_flake_polygons_flat()
            case ColorStyle.GRADIENT:
                return (
                    self.make_flake_gradients_defs(),
                    self.make_clean_flake_polygons_gradient(),
                )
            case _:
                raise Exception("Unknown ColorStyle")

    # TODO - @djacu see the other todo about the dict of points
    def make_flake_points(self):
        lambda_points_gap = self.ilambda.make_lambda_points()
        lambda_points_no_gap = self.ilambda.make_lambda_points(gap=0)

        translation_to_tip = Vector(tuple(-x for x in lambda_points_no_gap[1]))
        translation_left = Vector((-self.ilambda.radius, 0))
        translation = translation_to_tip + translation_left

        lambdas_translated = [point + translation for point in lambda_points_gap]
        flake_points = [
            Points([point.rotate(angle) for point in lambdas_translated])
            for angle in range(0, 360, 60)
        ]
        return flake_points

    def make_clean_flake_polygons_flat(self):
        flake_points = self.make_flake_points()

        return tuple(
            svg.Polygon(
                points=lambda_points.to_list(),
                fill=fill,
            )
            for lambda_points, fill in zip(
                flake_points, itertools.cycle(self.color_names)
            )
        )

    # TODO - @djacu see the other todo about the dict of points
    def make_gradient_end_points(self):
        lambda_points_no_gap = self.ilambda.make_lambda_points(gap=0)
        stop_point = lambda_points_no_gap[
            4
        ] + self.ilambda.radius * self.ilambda.thickness * Vector((1, 0))
        return {
            "x1": lambda_points_no_gap[0].x,
            "y1": lambda_points_no_gap[1].y,
            "x2": stop_point.x,
            "y2": stop_point.y,
        }

    def make_flake_gradients_defs(self):
        gradient_end_points = self.make_gradient_end_points()

        linear_gradients = []
        for color, color_name in zip(self.colors, self.color_names):
            color_original = color.convert("srgb").to_string(hex=True)
            color_midpoint = color.darken(1).convert("srgb").to_string(hex=True)
            color_dark = color.darken(2).convert("srgb").to_string(hex=True)

            linear_gradients.append(
                svg.LinearGradient(
                    id=color_name,
                    gradientUnits="userSpaceOnUse",
                    **gradient_end_points,
                    elements=[
                        svg.Stop(
                            offset=f"{self._gradient_stop_offsets[0]}%",
                            stop_color=color_dark,
                        ),
                        svg.Stop(
                            offset=f"{self._gradient_stop_offsets[1]}%",
                            stop_color=color_midpoint,
                        ),
                        svg.Stop(
                            offset=f"{self._gradient_stop_offsets[2]}%",
                            stop_color=color_original,
                        ),
                    ],
                )
            )
        return (svg.Defs(elements=linear_gradients),)

    def make_clean_flake_polygons_gradient(self):
        lambda_points_gap = self.ilambda.make_lambda_points()
        return tuple(
            svg.Polygon(
                points=lambda_points_gap.to_list(),
                fill=f"url(#{fill})",
                transform=[
                    svg.Translate(
                        1.25 * self.ilambda.radius * cosd(120),
                        1.25 * self.ilambda.radius * sind(120),
                    ),
                    svg.Rotate(
                        angle,
                        -1.25 * self.ilambda.radius * cosd(120),
                        -1.25 * self.ilambda.radius * sind(120),
                    ),
                ],
            )
            for angle, fill in zip(range(0, 360, 60), itertools.cycle(self.color_names))
        )
