import itertools
import math

import svg
from svg._types import Number

from .colors import NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE, Color, ColorStyle
from .geometry import Point, Points, Vector, cosd, sind
from .layout import ImageParameters


class Lambda:
    def __init__(
        self,
        image_parameters: ImageParameters | None = None,
        radius: int = 512,
        thickness: float = 1 / 4,
        gap: float = 1 / 32,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.image_parameters = image_parameters
        self.radius = radius
        self.thickness = thickness
        self.gap = gap

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

    def make_diagonal_line(self, radius: Number) -> list[Number]:
        hexagon_points = self.make_hexagon_points(radius)
        return Points([hexagon_points[1], hexagon_points[4]])

    def make_lambda_points(
        self,
        radius: Number | None = None,
        thickness: Number | None = None,
        gap: Number | None = None,
    ) -> Points:
        if radius is None:
            radius = self.radius
        if thickness is None:
            thickness = self.thickness
        if gap is None:
            gap = self.gap

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


class Logomark:
    def __init__(
        self,
        ilambda: Lambda,
        color_style: ColorStyle,
        image_parameters: ImageParameters | None = None,
        colors: tuple[Color] = (NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ilambda = ilambda
        self.colors = colors
        self.color_style = color_style
        self._make_color_names()
        self.image_parameters = image_parameters
        self._gradient_stop_offsets = [0, 25, 100]
        self.snowflake_lambda_ratio = 9 / 4

    @property
    def x_max(self):
        """The maximum x-value."""
        return self.ilambda.radius * self.snowflake_lambda_ratio

    @property
    def x_min(self):
        """The minimum x-value."""
        return -self.x_max

    @property
    def y_max(self):
        """The maximum y-value."""
        return self.x_max * math.sqrt(3) / 2

    @property
    def y_min(self):
        """The minimum y-value."""
        return -self.y_max

    @property
    def bounding_box(self):
        """The bounding box."""
        return (
            self.x_min,
            self.y_min,
            self.x_max,
            self.y_max,
        )

    @property
    def radius(self):
        """The snowflake radius."""
        return self.x_max

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

    # TODO: @djacu - use get_svg_elements and remove the two draw_clean_flake_* functions
    def draw_snowflake(self):
        match self.color_style:
            case ColorStyle.FLAT:
                return self.draw_clean_flake_flat()
            case ColorStyle.GRADIENT:
                return self.draw_clean_flake_gradient()
            case _:
                raise Exception("Unknown ColorStyle")

    def get_svg_elements(self):
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

    def make_flake_polygons_for_dimensions(self):
        flake_points = self.make_flake_points()

        return tuple(
            svg.Polygon(
                points=lambda_points.to_list(),
                stroke=self.ilambda.object_lines.stroke,
                stroke_width=self.ilambda.object_lines.stroke_width,
                fill=self.ilambda.object_lines.fill,
            )
            for lambda_points in flake_points
        )

    def make_clean_flake_polygons_flat(self):
        flake_points = self.make_flake_points()

        return [
            svg.Polygon(
                points=lambda_points.to_list(),
                fill=fill,
            )
            for lambda_points, fill in zip(
                flake_points, itertools.cycle(self.color_names)
            )
        ]

    def draw_clean_flake_flat(self) -> svg.SVG:
        return svg.SVG(
            viewBox=self.image_parameters.make_view_box(),
            elements=(self.make_clean_flake_polygons_flat()),
        )

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
        return [
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
        ]

    def draw_clean_flake_gradient(self) -> svg.SVG:
        return svg.SVG(
            viewBox=self.image_parameters.make_view_box(),
            elements=(
                self.make_flake_gradients_defs(),
                self.make_clean_flake_polygons_gradient(),
            ),
        )
