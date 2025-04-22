from dataclasses import dataclass

import svg

from .annotations import ConstructionLines, DimensionLines, LineGroup
from .geometry import Point
from .logomark import Lambda, Logomark
from .logotype import Logotype


class DimensionedLambda(Lambda):
    def __init__(
        self,
        object_lines: LineGroup,
        construction_lines: ConstructionLines,
        dimension_lines: DimensionLines,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.object_lines = object_lines
        self.construction_lines = construction_lines
        self.dimension_lines = dimension_lines

    def make_axis_lines(self):
        return (
            svg.Line(
                x1=self.canvas.min_x,
                x2=self.canvas.min_x + self.canvas.width,
                y1=0,
                y2=0,
                stroke="black",
            ),
            svg.Line(
                x1=0,
                x2=0,
                y1=self.canvas.min_y,
                y2=self.canvas.min_y + self.canvas.height,
                stroke="black",
            ),
        )

    def make_lambda_construction_lines(self):
        return (
            svg.Circle(
                cx=0,
                cy=0,
                r=self.radius,
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
            svg.Polygon(
                points=self.make_hexagon_points(radius=self.radius).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
        )

    def make_lambda_main_diagonal(self):
        return (
            svg.Polyline(
                points=self.make_diagonal_line(radius=self.radius).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
        )

    def make_lambda_linear_dimensions(self):
        hexagon_points = self.make_hexagon_points(radius=self.radius)
        lambda_points_no_gap = self.make_lambda_points(gap=0)
        lambda_points_gap = self.make_lambda_points()

        dim_main_diagonal = self.dimension_lines.make_dimension_line(
            point1=hexagon_points[1],
            point2=hexagon_points[4],
            flip=False,
            side="right",
            offset=1 / 2,
            reference=2 * self.radius,
        )

        dim_gap_diagonal = self.dimension_lines.make_dimension_line(
            point1=(lambda_points_gap[2] + lambda_points_gap[3]) / 2,
            point2=(lambda_points_gap[0] + lambda_points_gap[1]) / 2,
            flip=False,
            side="right",
            offset=15 / 32,
            reference=2 * self.radius,
        )
        dim_gap_long_edge = self.dimension_lines.make_dimension_line(
            point1=lambda_points_gap[1],
            point2=lambda_points_gap[2],
            flip=True,
            side="right",
            offset=7 / 16,
            reference=2 * self.radius,
        )
        dim_gap_left_top = self.dimension_lines.make_dimension_line(
            point1=lambda_points_gap[8],
            point2=lambda_points_gap[0],
            flip=False,
            side="right",
            offset=1 / 8,
            reference=2 * self.radius,
        )

        # fmt: off
        options = [
            {"side": "right", "flip": True,  "offset": 1 / 4},
            {"side": "right", "flip": True,  "offset": 15 / 32},
            {"side": "left",  "flip": True,  "offset": 1 / 4},
            {"side": "right", "flip": False, "offset": 1 / 4},
            {"side": "right", "flip": False, "offset": 1 / 4},
            {"side": "left",  "flip": True,  "offset": 1 / 2},
            {"side": "left",  "flip": True,  "offset": 1 / 2},
            {"side": "left",  "flip": False, "offset": 1 / 8},
            {"side": "left",  "flip": True,  "offset": 1 / 4},
        ]
        # fmt: on

        return (
            dim_main_diagonal,
            dim_gap_diagonal,
            dim_gap_long_edge,
            dim_gap_left_top,
        ) + tuple(
            self.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap[(index + 0) % 9],
                point2=lambda_points_no_gap[(index + 1) % 9],
                reference=2 * self.radius,
                **opts,
            )
            for index, opts in enumerate(options)
        )

    def make_lambda_angular_dimensions(self):
        lambda_points_no_gap = self.make_lambda_points()
        # fmt: off
        options = [
            {"flip": True,  "large": False, "side": "right", "ratio": 1 / 2, "text": "A"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "A"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 3 / 8, "text": "B"},
            {"flip": False, "large": False, "side": "right", "ratio": 1 / 2, "text": "A"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": False, "large": False, "side": "left",  "ratio": 1 / 2, "text": "B"},
            {"flip": True,  "large": False, "side": "left",  "ratio": 3 / 8, "text": "B"},
        ]
        # fmt: on

        return tuple(
            self.dimension_lines.make_dimension_angle(
                point1=lambda_points_no_gap[(index + 0) % 9],
                point2=lambda_points_no_gap[(index + 2) % 9],
                reference=lambda_points_no_gap[(index + 1) % 9],
                **opts,
            )
            for index, opts in enumerate(options)
        )

    def draw_lambda_linear_dimensions(self) -> svg.SVG:
        axis_lines = self.make_axis_lines()
        dimension_arrows = self.dimension_lines.make_dimension_arrow_defs()
        construction_lines = self.make_lambda_construction_lines()
        main_diagonal = self.make_lambda_main_diagonal()
        lambda_polygons = self.make_lambda_polygons()
        lambda_linear_dimensions = self.make_lambda_linear_dimensions()

        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=(
                axis_lines
                + dimension_arrows
                + construction_lines
                + main_diagonal
                + lambda_polygons
                + lambda_linear_dimensions
            ),
        )

    def draw_lambda_angular_dimensions(self) -> svg.SVG:
        axis_lines = self.make_axis_lines()
        dimension_arrows = self.dimension_lines.make_dimension_arrow_defs()
        construction_lines = self.make_lambda_construction_lines()
        main_diagonal = self.make_lambda_main_diagonal()
        lambda_polygons = self.make_lambda_polygons()
        lambda_angular_dimensions = self.make_lambda_angular_dimensions()

        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=(
                axis_lines
                + dimension_arrows
                + construction_lines
                + main_diagonal
                + lambda_polygons
                + lambda_angular_dimensions
            ),
        )


class DimensionedLogomark(Logomark):
    def __init__(
        self,
        object_lines: LineGroup,
        construction_lines: ConstructionLines,
        dimension_lines: DimensionLines,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.object_lines = object_lines
        self.construction_lines = construction_lines
        self.dimension_lines = dimension_lines

    def make_flake_construction_lines(self):
        return (
            svg.Circle(
                cx=0,
                cy=0,
                r=self.ilambda.radius * 2.25,
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
            svg.Polygon(
                points=self.ilambda.make_hexagon_points(
                    radius=self.ilambda.radius * 2.25
                ).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
            svg.Polyline(
                points=self.ilambda.make_diagonal_line(
                    radius=self.ilambda.radius * 2.25
                ).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
        )

    def make_flake_linear_dimensions(self):
        flake_points = self.make_flake_points()
        hexagon_points = self.ilambda.make_hexagon_points(radius=self.ilambda.radius)

        lin_inner_hex_long_length = self.dimension_lines.make_dimension_line(
            point1=hexagon_points[1],
            point2=hexagon_points[4],
            flip=False,
            side="right",
            offset=1 / 8,
            reference=2 * self.ilambda.radius,
        )

        lin_flake_long_length = self.dimension_lines.make_dimension_line(
            point1=flake_points[2][6],
            point2=flake_points[5][6],
            flip=True,
            side="right",
            offset=1 / 2,
            reference=2 * self.ilambda.radius,
        )

        return (
            lin_inner_hex_long_length,
            lin_flake_long_length,
        )

    def draw_flake_linear_dimensions(self) -> svg.SVG:
        axis_lines = self.ilambda.make_axis_lines()
        dimension_arrows = self.dimension_lines.make_dimension_arrow_defs()
        lambda_construction_lines = self.ilambda.make_lambda_construction_lines()
        construction_lines = self.make_flake_construction_lines()
        linear_dimensions = self.make_flake_linear_dimensions()

        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=(
                self.make_flake_polygons_for_dimensions()
                + axis_lines
                + dimension_arrows
                + lambda_construction_lines
                + construction_lines
                + linear_dimensions
            ),
        )

    def draw_lambda_with_gradients_line(self) -> svg.SVG:
        gradient_end_points = self.make_gradient_end_points()
        point_start = Point((gradient_end_points["x1"], gradient_end_points["y1"]))
        point_stop = Point((gradient_end_points["x2"], gradient_end_points["y2"]))
        point_vector = point_stop - point_start
        stop_points = [
            point_start + offset / 100 * point_vector
            for offset in self._gradient_stop_offsets
        ]

        lambda_points_no_gap = self.ilambda.make_lambda_points(gap=0)
        dimension_lines = [
            self.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap[0],
                point2=point_start,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.ilambda.radius,
                text="V",
            ),
            self.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap[1],
                point2=point_start,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.ilambda.radius,
                text="H",
            ),
            self.dimension_lines.make_dimension_line(
                point1=lambda_points_no_gap[4],
                point2=point_stop,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.ilambda.radius,
                text="H",
            ),
        ]

        gradient_lines = tuple(
            [
                svg.Line(
                    **gradient_end_points,
                    stroke=self.construction_lines.stroke,
                    stroke_width=self.construction_lines.stroke_width,
                    stroke_dasharray=self.construction_lines.stroke_dasharray,
                ),
            ]
            + [
                svg.Circle(
                    cx=stop_point.x,
                    cy=stop_point.y,
                    r=2 * self.construction_lines.stroke_width,
                    fill=self.construction_lines.stroke,
                )
                for stop_point in stop_points
            ]
            + [
                svg.Text(
                    x=stop_point.x,
                    y=stop_point.y,
                    dx=f"{0.01 * self.ilambda.radius}",
                    dy=f"-{0.01 * self.ilambda.radius}",
                    elements=[f"{offset}%"],
                    font_size=self.construction_lines.font_size,
                )
                for stop_point, offset in zip(stop_points, self._gradient_stop_offsets)
            ]
            + dimension_lines
        )

        axis_lines = self.ilambda.make_axis_lines()
        dimension_arrows = self.dimension_lines.make_dimension_arrow_defs()
        construction_lines = self.ilambda.make_lambda_construction_lines()
        lambda_polygons = self.ilambda.make_lambda_polygons()

        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=(
                self.make_flake_gradients_defs()
                + axis_lines
                + dimension_arrows
                + construction_lines
                + lambda_polygons
                + gradient_lines
            ),
        )

    def draw_lambda_with_gradients_background(self) -> svg.SVG:
        gradient_end_points = self.make_gradient_end_points()
        point_start = Point((gradient_end_points["x1"], gradient_end_points["y1"]))
        point_stop = Point((gradient_end_points["x2"], gradient_end_points["y2"]))
        point_vector = point_stop - point_start
        stop_points = [
            point_start + offset / 100 * point_vector
            for offset in self._gradient_stop_offsets
        ]

        gradient_lines = tuple(
            [
                svg.Line(
                    **gradient_end_points,
                    stroke=self.construction_lines.stroke,
                    stroke_width=self.construction_lines.stroke_width,
                    stroke_dasharray=self.construction_lines.stroke_dasharray,
                ),
            ]
            + [
                svg.Circle(
                    cx=stop_point.x,
                    cy=stop_point.y,
                    r=2 * self.construction_lines.stroke_width,
                    fill=self.construction_lines.stroke,
                )
                for stop_point in stop_points
            ]
            + [
                svg.Text(
                    x=stop_point.x,
                    y=stop_point.y,
                    dx=f"{0.01 * self.ilambda.radius}",
                    dy=f"-{0.01 * self.ilambda.radius}",
                    elements=[f"{offset}%"],
                    font_size=self.construction_lines.font_size,
                )
                for stop_point, offset in zip(stop_points, self._gradient_stop_offsets)
            ]
        )

        background = self.canvas.make_svg_background(
            fill=f"url(#{self.color_names[0]})"
        )
        axis_lines = self.ilambda.make_axis_lines()
        dimension_arrows = self.dimension_lines.make_dimension_arrow_defs()
        construction_lines = self.ilambda.make_lambda_construction_lines()
        lambda_polygons = self.ilambda.make_lambda_polygons()

        return svg.SVG(
            viewBox=self.canvas.make_view_box(),
            elements=(
                self.make_flake_gradients_defs()
                + background
                + axis_lines
                + dimension_arrows
                + construction_lines
                + lambda_polygons
                + gradient_lines
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
