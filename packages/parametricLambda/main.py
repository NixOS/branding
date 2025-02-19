import fractions
import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import svg
from coloraide import Color
from svg._types import Number


def cosd(angle) -> float:
    return math.cos(math.radians(angle))


def sind(angle) -> float:
    return math.sin(math.radians(angle))


NIXOS_DARK_BLUE = Color("oklch", (0.58, 0.125, 260))
NIXOS_LIGHT_BLUE = Color("oklch", (0.76, 0.090, 240))


class Point(Sequence):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return f"{self.x, self.y}"

    def __repr__(self):
        return f"Point{self.value}"

    def __add__(self, other: Self | "Vector") -> Self:
        if isinstance(other, Point):
            return Point((self.x + other.x, self.y + other.y))
        elif isinstance(other, Vector):
            return Point((self.x + other[0], self.y + other[1]))
        else:
            raise Exception(f"Not sure how to add {type(other)} to Point.")

    def __sub__(self, other: Self | "Vector") -> Self:
        if isinstance(other, Point):
            return Vector((self.x - other.x, self.y - other.y))
        elif isinstance(other, Vector):
            return Point((self.x - other[0], self.y - other[1]))
        else:
            raise Exception(f"Not sure how to add {type(other)} to Point.")

    def __truediv__(self, other: Number) -> Self:
        return Point(tuple(elem / other for elem in self))

    @property
    def x(self):
        """The x property."""
        return self.value[0]

    @property
    def y(self):
        """The y property."""
        return self.value[1]

    def distance(self, other: Self) -> float:
        return (self - other).length()

    def normal(self, reference: Self):
        normal = Vector(
            (
                +(self.y - reference.y),
                -(self.x - reference.x),
            )
        )
        return normal.normalize()

    def rotate(self, angle: Number):
        rotation_matrix = Matrix(
            (
                Vector(
                    (cosd(angle), sind(-angle)),
                ),
                Vector(
                    (sind(angle), cosd(angle)),
                ),
            )
        )
        return Point(rotation_matrix @ self)


class Points(Sequence):
    def __init__(self, value: list[Point]):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return f"Points{self.value}"

    def __str__(self):
        return "[" + ", ".join(str(elem) for elem in self.value) + "]"

    def to_list(self):
        nested = [(elem.x, elem.y) for elem in self]
        return [elem for point in nested for elem in point]


class Vector(Sequence):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return f"Vector{self.value}"

    def __str__(self):
        return f"{self.value}"

    def __add__(self, other: Self) -> Self:
        return Vector(tuple(s + o for s, o in zip(self, other)))

    def __neg__(self):
        return Vector(tuple(-elem for elem in self))

    def __sub__(self, other: Self) -> Self:
        return self + (-other)

    def __mul__(self, other: Self) -> Self:
        return Vector(tuple(s * o for s, o in zip(self, other)))

    def __rmul__(self, other: Number) -> Self:
        return Vector(tuple(other * elem for elem in self))

    def __matmul__(self, other: Self | Point) -> Self:
        if isinstance(other, Point | Vector):
            return [s * o for s, o in zip(self, other)]
        else:
            raise Exception(f"Not sure how to add {type(other)} to Point.")

    def __truediv__(self, other: Number) -> Self:
        return Vector(tuple(elem / other for elem in self))

    def _modulus_squared(self) -> Number:
        return self.dot(self)

    def length(self) -> float:
        return math.sqrt(self._modulus_squared())

    def dot(self, other: Self) -> float:
        return sum((self * other))

    def normalize(self) -> Self:
        return self / self.length()

    def normal(self) -> Self:
        return Vector((self[1], -self[0])).normalize()

    def angle_from(self, other: Self) -> float:
        return math.acos(self.dot(other) / (self.length() * other.length()))

    def to_point(self) -> Point:
        return Point(self.value)


class Matrix(Sequence):
    def __init__(self, value: Sequence[Vector]):
        self.value = value
        super().__init__()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value) * len(self.value[0])

    def __str__(self):
        return "(" + ",\n ".join(str(elem) for elem in self.value) + ")"

    def transpose(self) -> Self:
        return Matrix(tuple(zip(*self)))

    def __matmul__(self, other: Point | Vector) -> Self:
        if isinstance(other, Point | Vector):
            return [sum(row @ other) for row in self]
        else:
            raise Exception(
                f"Not sure how to matrix multiply {type(self)} and {type(other)}."
            )


@dataclass
class LineGroup:
    name: str
    stroke: str
    stroke_width: int
    font_size: str
    stroke_dasharray: int = 4
    fill: str = "transparent"


class ConstructionLines:
    def __init__(self, construction_lines: LineGroup, **kwargs):
        super().__init__(**kwargs)
        self.construction_lines = construction_lines


class DimensionLines:
    def __init__(self, dimension_lines: LineGroup, **kwargs):
        super().__init__(**kwargs)
        self.dimension_lines = dimension_lines

    def make_dimension_line(
        self,
        point1,
        point2,
        flip=False,
        side="left",
        offset=1,
        reference=1,
        text=None,
    ):
        if flip:
            point1, point2 = point2, point1

        measured_line = point1 - point2
        normal = measured_line.normal()
        distance = offset * measured_line.length()

        point1_end = point1 + 1.25 * distance * normal
        point2_end = point2 + 1.25 * distance * normal
        point1_dim = point1 + 1.20 * distance * normal
        point2_dim = point2 + 1.20 * distance * normal

        text_offset = 1.19 if side == "left" else 1.21
        point1_text = point1 + text_offset * distance * normal
        point2_text = point2 + text_offset * distance * normal

        hash_args = locals()
        hash_args.pop("self")
        input_hash = hash(frozenset(hash_args.items()))

        if text is None:
            text = fractions.Fraction(round(measured_line.length()), reference)

        return [
            svg.Line(
                x1=point1.x,
                y1=point1.y,
                x2=point1_end.x,
                y2=point1_end.y,
                stroke=self.dimension_lines.stroke,
                stroke_width=self.dimension_lines.stroke_width,
            ),
            svg.Line(
                x1=point2.x,
                y1=point2.y,
                x2=point2_end.x,
                y2=point2_end.y,
                stroke=self.dimension_lines.stroke,
                stroke_width=self.dimension_lines.stroke_width,
            ),
            svg.Line(
                x1=point1_dim.x,
                y1=point1_dim.y,
                x2=point2_dim.x,
                y2=point2_dim.y,
                stroke=self.dimension_lines.stroke,
                stroke_width=self.dimension_lines.stroke_width,
                marker_start="url(#dimension-arrow-head)",
                marker_end="url(#dimension-arrow-head)",
            ),
            svg.Path(
                id=f"dimension_path_{input_hash}",
                d=[
                    svg.M(point1_text.x, point1_text.y),
                    svg.L(point2_text.x, point2_text.y),
                ],
            ),
            svg.Text(
                font_size=self.dimension_lines.font_size,
                elements=[
                    svg.TextPath(
                        href=f"#dimension_path_{input_hash}",
                        text=text,
                        startOffset="50%",
                        text_anchor="middle",
                        side=side,
                    ),
                ],
            ),
        ]

    def make_dimension_angle(
        self,
        point1,
        point2,
        reference,
        flip,
        large,
        side,
        ratio,
        text=None,
    ):
        if flip:
            point1, point2 = point2, point1

        vector1 = point1 - reference
        vector2 = point2 - reference

        shorter_length = min(vector1.length(), vector2.length())
        arc_radius = shorter_length / 2

        mid_point_1 = reference + shorter_length * ratio * vector1.normalize()
        mid_point_2 = reference + shorter_length * ratio * vector2.normalize()

        input_hash = hash((point1, point2, reference, flip, large, text, side, ratio))

        if text is None:
            text = f"{round(math.degrees(vector1.angle_from(vector2)))}°"

        return [
            svg.Path(
                id=f"dimension_angle_{input_hash}",
                d=[
                    svg.M(
                        mid_point_1.x,
                        mid_point_1.y,
                    ),
                    svg.Arc(
                        arc_radius,
                        arc_radius,
                        0,
                        large,
                        True,
                        mid_point_2.x,
                        mid_point_2.y,
                    ),
                ],
                stroke=self.dimension_lines.stroke,
                stroke_width=self.dimension_lines.stroke_width,
                fill=self.dimension_lines.fill,
                marker_start="url(#dimension-arrow-head)",
                marker_end="url(#dimension-arrow-head)",
            ),
            svg.Text(
                font_size=self.dimension_lines.font_size,
                elements=[
                    svg.TextPath(
                        href=f"#dimension_angle_{input_hash}",
                        text=text,
                        startOffset="50%",
                        text_anchor="middle",
                        side=side,
                    ),
                ],
            ),
        ]

    def make_dimension_arrow_defs(self):
        return [
            svg.Defs(
                elements=[
                    svg.Marker(
                        id="dimension-arrow-head",
                        orient="auto-start-reverse",
                        markerWidth=20,
                        markerHeight=20,
                        refX=20,
                        refY=5,
                        elements=[
                            svg.Path(
                                d=[svg.M(0, 0), svg.v(10), svg.L(20, 5), svg.Z()],
                                fill=self.dimension_lines.stroke,  # can't use fill because of arcs
                            )
                        ],
                    )
                ]
            )
        ]


class ImageParameters:
    def __init__(
        self,
        min_x: int,
        min_y: int,
        width: int,
        height: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.min_x = min_x
        self.min_y = min_y
        self.width = width
        self.height = height

    def make_view_box(self):
        return svg.ViewBoxSpec(
            min_x=self.min_x,
            min_y=self.min_y,
            width=self.width,
            height=self.height,
        )


class Lambda(ConstructionLines, DimensionLines, ImageParameters):
    def __init__(
        self,
        object_lines: LineGroup,
        radius: int = 512,
        thickness: float = 1 / 4,
        gap: float = 1 / 32,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.object_lines = object_lines
        self.radius = radius
        self.thickness = thickness
        self.gap = gap

    @staticmethod
    def make_hexagon_points(radius: Number) -> Points:
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

    @staticmethod
    def make_diagonal_line(radius: Number) -> list[Number]:
        hexagon_points = Lambda.make_hexagon_points(radius)
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

        hexagon_points = Lambda.make_hexagon_points(radius)
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
        return [
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
        ]

    def make_axis_lines(self):
        return [
            svg.Line(
                x1=self.min_x,
                x2=self.min_x + self.width,
                y1=0,
                y2=0,
                stroke="black",
            ),
            svg.Line(
                x1=0,
                x2=0,
                y1=self.min_y,
                y2=self.min_y + self.height,
                stroke="black",
            ),
        ]

    def make_lambda_construction_lines(self):
        return [
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
        ]

    def make_lambda_main_diagonal(self):
        return [
            svg.Polyline(
                points=Lambda.make_diagonal_line(radius=self.radius).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
        ]

    def make_lambda_linear_dimensions(self):
        hexagon_points = self.make_hexagon_points(radius=self.radius)
        lambda_points_no_gap = self.make_lambda_points(gap=0)
        lambda_points_gap = self.make_lambda_points()

        dim_main_diagonal = self.make_dimension_line(
            point1=hexagon_points[1],
            point2=hexagon_points[4],
            flip=False,
            side="right",
            offset=1 / 2,
            reference=2 * self.radius,
        )

        dim_gap_diagonal = self.make_dimension_line(
            point1=(lambda_points_gap[2] + lambda_points_gap[3]) / 2,
            point2=(lambda_points_gap[0] + lambda_points_gap[1]) / 2,
            flip=False,
            side="right",
            offset=15 / 32,
            reference=2 * self.radius,
        )
        dim_gap_long_edge = self.make_dimension_line(
            point1=lambda_points_gap[1],
            point2=lambda_points_gap[2],
            flip=True,
            side="right",
            offset=7 / 16,
            reference=2 * self.radius,
        )
        dim_gap_left_top = self.make_dimension_line(
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

        return [
            dim_main_diagonal,
            dim_gap_diagonal,
            dim_gap_long_edge,
            dim_gap_left_top,
        ] + [
            self.make_dimension_line(
                point1=lambda_points_no_gap[(index + 0) % 9],
                point2=lambda_points_no_gap[(index + 1) % 9],
                reference=2 * self.radius,
                **opts,
            )
            for index, opts in enumerate(options)
        ]

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

        return [
            self.make_dimension_angle(
                point1=lambda_points_no_gap[(index + 0) % 9],
                point2=lambda_points_no_gap[(index + 2) % 9],
                reference=lambda_points_no_gap[(index + 1) % 9],
                **opts,
            )
            for index, opts in enumerate(options)
        ]

    def draw_lambda_linear_dimensions(self) -> svg.SVG:
        axis_lines = self.make_axis_lines()
        dimension_arrows = self.make_dimension_arrow_defs()
        construction_lines = self.make_lambda_construction_lines()
        main_diagonal = self.make_lambda_main_diagonal()
        lambda_polygons = self.make_lambda_polygons()
        lambda_linear_dimensions = self.make_lambda_linear_dimensions()

        return svg.SVG(
            viewBox=self.make_view_box(),
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
        dimension_arrows = self.make_dimension_arrow_defs()
        construction_lines = self.make_lambda_construction_lines()
        main_diagonal = self.make_lambda_main_diagonal()
        lambda_polygons = self.make_lambda_polygons()
        lambda_angular_dimensions = self.make_lambda_angular_dimensions()

        return svg.SVG(
            viewBox=self.make_view_box(),
            elements=(
                axis_lines
                + dimension_arrows
                + construction_lines
                + main_diagonal
                + lambda_polygons
                + lambda_angular_dimensions
            ),
        )

    def write_dimensioned_lambda(self) -> None:
        with open(Path("nixos-lambda-dimensioned-linear.svg"), "w") as file:
            file.write(str(self.draw_lambda_linear_dimensions()))
        with open(Path("nixos-lambda-dimensioned-angular.svg"), "w") as file:
            file.write(str(self.draw_lambda_angular_dimensions()))


class SnowFlake(Lambda, ConstructionLines, DimensionLines, ImageParameters):
    def __init__(
        self,
        colors: tuple[Color] = (NIXOS_DARK_BLUE, NIXOS_LIGHT_BLUE),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.colors = colors
        self._make_color_names()

    def _make_color_names(self):
        self.color_names = tuple(color.to_string() for color in self.colors)

    def make_flake_points(self):
        lambda_points_gap = self.make_lambda_points()
        lambda_points_no_gap = self.make_lambda_points(gap=0)

        translation_to_tip = Vector(tuple(-x for x in lambda_points_no_gap[1]))
        translation_left = Vector((-self.radius, 0))
        translation = translation_to_tip + translation_left

        lambdas_translated = [point + translation for point in lambda_points_gap]
        flake_points = [
            Points([point.rotate(angle) for point in lambdas_translated])
            for angle in range(0, 360, 60)
        ]
        return flake_points

    def make_flake_polygons_for_dimensions(self):
        flake_points = self.make_flake_points()

        return [
            svg.Polygon(
                points=lambda_points.to_list(),
                stroke=self.object_lines.stroke,
                stroke_width=self.object_lines.stroke_width,
                fill=self.object_lines.fill,
            )
            for lambda_points in flake_points
        ]

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

    def make_flake_construction_lines(self):
        return [
            svg.Circle(
                cx=0,
                cy=0,
                r=self.radius * 2.25,
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
            svg.Polygon(
                points=self.make_hexagon_points(radius=self.radius * 2.25).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
            svg.Polyline(
                points=Lambda.make_diagonal_line(radius=self.radius * 2.25).to_list(),
                stroke=self.construction_lines.stroke,
                stroke_width=self.construction_lines.stroke_width,
                stroke_dasharray=self.construction_lines.stroke_dasharray,
                fill=self.construction_lines.fill,
            ),
        ]

    def make_flake_linear_dimensions(self):
        flake_points = self.make_flake_points()
        hexagon_points = self.make_hexagon_points(radius=self.radius)

        lin_inner_hex_long_length = self.make_dimension_line(
            point1=hexagon_points[1],
            point2=hexagon_points[4],
            flip=False,
            side="right",
            offset=1 / 8,
            reference=2 * self.radius,
        )

        lin_flake_long_length = self.make_dimension_line(
            point1=flake_points[2][6],
            point2=flake_points[5][6],
            flip=True,
            side="right",
            offset=1 / 2,
            reference=2 * self.radius,
        )

        return [
            lin_inner_hex_long_length,
            lin_flake_long_length,
        ]

    def draw_flake_linear_dimensions(self) -> svg.SVG:
        axis_lines = self.make_axis_lines()
        dimension_arrows = self.make_dimension_arrow_defs()
        lambda_construction_lines = self.make_lambda_construction_lines()
        construction_lines = self.make_flake_construction_lines()
        linear_dimensions = self.make_flake_linear_dimensions()

        return svg.SVG(
            viewBox=self.make_view_box(),
            elements=(
                self.make_flake_polygons_for_dimensions()
                + axis_lines
                + dimension_arrows
                + lambda_construction_lines
                + construction_lines
                + linear_dimensions
            ),
        )

    def draw_clean_flake_flat(self) -> svg.SVG:
        return svg.SVG(
            viewBox=self.make_view_box(),
            elements=(self.make_clean_flake_polygons_flat()),
        )

    def write_dimensioned_flake(self) -> None:
        with open(Path("nixos-snowflake-dimensioned-linear.svg"), "w") as file:
            file.write(str(self.draw_flake_linear_dimensions()))

    def write_clean_flake_flat(self) -> None:
        with open(Path("nixos-snowflake-color-flat.svg"), "w") as file:
            file.write(str(self.draw_clean_flake_flat()))


class SnowFlakeGradient(SnowFlake):
    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._make_color_names()
        self._gradient_stop_offsets = [0, 25, 100]
        self._gradient_lightness_delta = -0.04
        self._gradient_chroma_delta = -0.01

    def _make_color_names(self):
        self.color_names = tuple(
            f"linear-gradient-{hash(color.to_string())}" for color in self.colors
        )

    def darken(self, color: Color) -> Color:
        # fmt: off
        return (
            color.clone()
            .set("lightness", lambda lightness: lightness + self._gradient_lightness_delta )
            .set("chroma", lambda chroma: chroma + self._gradient_chroma_delta)
        )
        # fmt: on

    def make_gradient_end_points(self):
        lambda_points_no_gap = self.make_lambda_points(gap=0)
        stop_point = lambda_points_no_gap[4] + self.radius * self.thickness * Vector(
            (1, 0)
        )
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
            color_midpoint = self.darken(color).convert("srgb").to_string(hex=True)
            color_dark = (
                self.darken(self.darken(color)).convert("srgb").to_string(hex=True)
            )

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
        return [
            svg.Defs(elements=linear_gradients),
        ]

    def make_clean_flake_polygons_gradient(self):
        lambda_points_gap = self.make_lambda_points()
        return [
            svg.Polygon(
                points=lambda_points_gap.to_list(),
                fill=f"url(#{fill})",
                transform=[
                    svg.Translate(
                        1.25 * self.radius * cosd(120),
                        1.25 * self.radius * sind(120),
                    ),
                    svg.Rotate(
                        angle,
                        -1.25 * self.radius * cosd(120),
                        -1.25 * self.radius * sind(120),
                    ),
                ],
            )
            for angle, fill in zip(range(0, 360, 60), itertools.cycle(self.color_names))
        ]

    def draw_lambda_with_gradients_line(self) -> svg.SVG:
        gradient_end_points = self.make_gradient_end_points()
        point_start = Point((gradient_end_points["x1"], gradient_end_points["y1"]))
        point_stop = Point((gradient_end_points["x2"], gradient_end_points["y2"]))
        point_vector = point_stop - point_start
        stop_points = [
            point_start + offset / 100 * point_vector
            for offset in self._gradient_stop_offsets
        ]

        lambda_points_no_gap = self.make_lambda_points(gap=0)
        dimension_lines = [
            self.make_dimension_line(
                point1=lambda_points_no_gap[0],
                point2=point_start,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.radius,
                text="V",
            ),
            self.make_dimension_line(
                point1=lambda_points_no_gap[1],
                point2=point_start,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.radius,
                text="H",
            ),
            self.make_dimension_line(
                point1=lambda_points_no_gap[4],
                point2=point_stop,
                flip=False,
                side="left",
                offset=0,
                reference=2 * self.radius,
                text="H",
            ),
        ]

        gradient_lines = (
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
                    dx=f"{0.01 * self.radius}",
                    dy=f"-{0.01 * self.radius}",
                    elements=[f"{offset}%"],
                    font_size=self.construction_lines.font_size,
                )
                for stop_point, offset in zip(stop_points, self._gradient_stop_offsets)
            ]
            + dimension_lines
        )

        axis_lines = self.make_axis_lines()
        dimension_arrows = self.make_dimension_arrow_defs()
        construction_lines = self.make_lambda_construction_lines()
        lambda_polygons = self.make_lambda_polygons()

        return svg.SVG(
            viewBox=self.make_view_box(),
            elements=(
                self.make_flake_gradients_defs()
                + axis_lines
                + dimension_arrows
                + construction_lines
                + lambda_polygons
                + gradient_lines
            ),
        )

    def write_lambda_with_gradient_line(self) -> None:
        with open(Path("nixos-lambda-dimensioned-gradient.svg"), "w") as file:
            file.write(str(self.draw_lambda_with_gradients_line()))

    def draw_lambda_with_gradients_background(self) -> svg.SVG:
        gradient_end_points = self.make_gradient_end_points()
        point_start = Point((gradient_end_points["x1"], gradient_end_points["y1"]))
        point_stop = Point((gradient_end_points["x2"], gradient_end_points["y2"]))
        point_vector = point_stop - point_start
        stop_points = [
            point_start + offset / 100 * point_vector
            for offset in self._gradient_stop_offsets
        ]

        gradient_lines = (
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
                    dx=f"{0.01 * self.radius}",
                    dy=f"-{0.01 * self.radius}",
                    elements=[f"{offset}%"],
                    font_size=self.construction_lines.font_size,
                )
                for stop_point, offset in zip(stop_points, self._gradient_stop_offsets)
            ]
        )

        background = [
            svg.Rect(
                x=self.min_x,
                y=self.min_y,
                width=self.width,
                height=self.height,
                fill=f"url(#{self.color_names[0]})",
            )
        ]

        axis_lines = self.make_axis_lines()
        dimension_arrows = self.make_dimension_arrow_defs()
        construction_lines = self.make_lambda_construction_lines()
        lambda_polygons = self.make_lambda_polygons()

        return svg.SVG(
            viewBox=self.make_view_box(),
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

    def write_lambda_with_gradient_background(self) -> None:
        with open(Path("nixos-lambda-background-gradient.svg"), "w") as file:
            file.write(str(self.draw_lambda_with_gradients_background()))

    def draw_clean_flake_gradient(self) -> svg.SVG:
        return svg.SVG(
            viewBox=self.make_view_box(),
            elements=(
                self.make_flake_gradients_defs(),
                self.make_clean_flake_polygons_gradient(),
            ),
        )

    def write_clean_flake_gradient(self) -> None:
        with open(Path("nixos-snowflake-color-gradient.svg"), "w") as file:
            file.write(str(self.draw_clean_flake_gradient()))


def make_dimensioned_lambdas() -> None:
    object_lines = LineGroup(
        name="object",
        stroke="green",
        stroke_width=4,
        font_size="2rem",
    )
    construction_lines = LineGroup(
        name="construction",
        stroke="blue",
        stroke_width=2,
        font_size="2rem",
    )
    dimension_lines = LineGroup(
        name="dimension",
        stroke="red",
        stroke_width=1,
        font_size="2rem",
    )
    radius = 512
    lambda_inst = Lambda(
        object_lines=object_lines,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
        min_x=-2 * radius,
        min_y=-2 * radius,
        width=4 * radius,
        height=4 * radius,
        radius=radius,
        thickness=1 / 4,
        gap=1 / 32,
    )
    lambda_inst.write_dimensioned_lambda()


def make_dimensioned_snowflake() -> None:
    object_lines = LineGroup(
        name="object",
        stroke="green",
        stroke_width=8,
        font_size="4rem",
    )
    construction_lines = LineGroup(
        name="construction",
        stroke="blue",
        stroke_width=4,
        font_size="4rem",
    )
    dimension_lines = LineGroup(
        name="dimension",
        stroke="red",
        stroke_width=2,
        font_size="4rem",
    )
    radius = 512
    snow_flake = SnowFlake(
        object_lines=object_lines,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
        min_x=-4 * radius,
        min_y=-4 * radius,
        width=8 * radius,
        height=8 * radius,
        radius=radius,
        thickness=1 / 4,
        gap=1 / 32,
    )
    snow_flake.write_dimensioned_flake()


def make_lambda_gradient_line() -> None:
    object_lines = LineGroup(
        name="object",
        stroke="green",
        stroke_width=4,
        font_size="2rem",
    )
    construction_lines = LineGroup(
        name="construction",
        stroke="blue",
        stroke_width=2,
        font_size="2rem",
    )
    dimension_lines = LineGroup(
        name="dimension",
        stroke="red",
        stroke_width=1,
        font_size="2rem",
    )
    radius = 512
    snow_flake = SnowFlakeGradient(
        object_lines=object_lines,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
        min_x=-2 * radius,
        min_y=-2 * radius,
        width=4 * radius,
        height=4 * radius,
        radius=radius,
        thickness=1 / 4,
        gap=1 / 32,
    )
    snow_flake.write_lambda_with_gradient_line()


def make_lambda_gradient_background() -> None:
    object_lines = LineGroup(
        name="object",
        stroke="white",
        stroke_width=4,
        font_size="2rem",
        fill="transparent",
    )
    construction_lines = LineGroup(
        name="construction",
        stroke="black",
        stroke_width=2,
        font_size="2rem",
    )
    dimension_lines = LineGroup(
        name="dimension",
        stroke="red",
        stroke_width=1,
        font_size="2rem",
    )
    radius = 512
    snow_flake = SnowFlakeGradient(
        object_lines=object_lines,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
        min_x=-2 * radius,
        min_y=-2 * radius,
        width=4 * radius,
        height=4 * radius,
        radius=radius,
        thickness=1 / 4,
        gap=1 / 32,
    )
    snow_flake.write_lambda_with_gradient_background()


def make_snowflake_flat() -> None:
    object_lines = None
    construction_lines = None
    dimension_lines = None
    radius = 512
    snow_flake = SnowFlake(
        object_lines=object_lines,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
        min_x=-2.25 * radius,
        min_y=-2.25 * radius,
        width=4.5 * radius,
        height=4.5 * radius,
        radius=radius,
        thickness=1 / 4,
        gap=1 / 32,
    )
    snow_flake.write_clean_flake_flat()


def make_snowflake_gradient() -> None:
    object_lines = None
    construction_lines = None
    dimension_lines = None
    radius = 512
    snow_flake = SnowFlakeGradient(
        object_lines=object_lines,
        construction_lines=construction_lines,
        dimension_lines=dimension_lines,
        min_x=-2.25 * radius,
        min_y=-2.25 * radius,
        width=4.5 * radius,
        height=4.5 * radius,
        radius=radius,
        thickness=1 / 4,
        gap=1 / 32,
    )
    snow_flake.write_clean_flake_gradient()


def main():
    make_dimensioned_lambdas()
    make_dimensioned_snowflake()
    make_lambda_gradient_line()
    make_lambda_gradient_background()
    make_snowflake_flat()
    make_snowflake_gradient()


if __name__ == "__main__":
    main()
