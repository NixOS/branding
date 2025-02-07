import fractions
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Self

import svg
from svg._types import Number


def make_hexagon_points(radius: Number) -> list[Number]:
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


def make_diagonal_line(radius: Number) -> list[Number]:
    hexagon_points = make_hexagon_points(radius)
    return Points([hexagon_points[1], hexagon_points[4]])


def cosd(angle) -> float:
    return math.cos(math.radians(angle))


def sind(angle) -> float:
    return math.sin(math.radians(angle))


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
        return Vector((s + o for s, o in zip(self, other)))

    def __neg__(self):
        return Vector(tuple(-elem for elem in self))

    def __sub__(self, other: Self) -> Self:
        return self + (-other)

    def __mul__(self, other: Self) -> Self:
        return Vector(tuple(s * o for s, o in zip(self, other)))

    def __rmul__(self, other: Number) -> Self:
        return Vector(tuple(other * elem for elem in self))

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


def make_dimension_line(point1, point2, side, offset, parameters, text=None):
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

    input_hash = hash((point1, point2, side, text, offset))

    if text is None:
        text = fractions.Fraction(round(measured_line.length()), 2 * parameters.radius)

    return [
        svg.Line(
            x1=point1.x,
            y1=point1.y,
            x2=point1_end.x,
            y2=point1_end.y,
            stroke=parameters.dimension_lines.stroke,
            stroke_width=parameters.dimension_lines.stroke_width,
        ),
        svg.Line(
            x1=point2.x,
            y1=point2.y,
            x2=point2_end.x,
            y2=point2_end.y,
            stroke=parameters.dimension_lines.stroke,
            stroke_width=parameters.dimension_lines.stroke_width,
        ),
        svg.Line(
            x1=point1_dim.x,
            y1=point1_dim.y,
            x2=point2_dim.x,
            y2=point2_dim.y,
            stroke=parameters.dimension_lines.stroke,
            stroke_width=parameters.dimension_lines.stroke_width,
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
            font_size="2rem",
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
            stroke="red",
            fill="transparent",
            marker_start="url(#dimension-arrow-head)",
            marker_end="url(#dimension-arrow-head)",
        ),
        svg.Text(
            font_size="2rem",
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


def make_lambda_points(radius: Number, thickness: Number, gap: Number) -> list[Number]:
    hexagon_points = make_hexagon_points(radius)
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


def make_dimension_arrow_defs():
    return svg.Defs(
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
                        fill="red",
                    )
                ],
            )
        ]
    )


def make_lambda_construction_lines(parameters):
    return [
        svg.Line(
            x1=parameters.image_parameters.min_x,
            x2=parameters.image_parameters.min_x + parameters.image_parameters.width,
            y1=0,
            y2=0,
            stroke="black",
        ),
        svg.Line(
            x1=0,
            x2=0,
            y1=parameters.image_parameters.min_y,
            y2=parameters.image_parameters.min_y + parameters.image_parameters.height,
            stroke="black",
        ),
        svg.Circle(
            cx=0,
            cy=0,
            r=parameters.radius,
            stroke=parameters.construction_lines.stroke,
            stroke_width=parameters.construction_lines.stroke_width,
            stroke_dasharray=4,
            fill="transparent",
        ),
        svg.Polygon(
            points=make_hexagon_points(radius=parameters.radius).to_list(),
            stroke=parameters.construction_lines.stroke,
            stroke_width=parameters.construction_lines.stroke_width,
            stroke_dasharray=4,
            fill="transparent",
        ),
        svg.Polyline(
            points=make_diagonal_line(radius=parameters.radius).to_list(),
            stroke=parameters.construction_lines.stroke,
            stroke_width=parameters.construction_lines.stroke_width,
            stroke_dasharray=4,
            fill="transparent",
        ),
    ]


@dataclass
class LineGroup:
    name: str
    stroke: str
    stroke_width: int


@dataclass
class ImageParameters:
    min_x = -1100
    min_y = -1100
    width = 2200
    height = 2200


@dataclass
class Parameters:
    radius = 512
    thickness = 1 / 4
    gap = 1 / 16
    object_lines: LineGroup
    construction_lines: LineGroup
    dimension_lines: LineGroup
    image_parameters: ImageParameters


def draw(parameters) -> svg.SVG:
    hexagon_points = make_hexagon_points(radius=parameters.radius)
    lambda_points = make_lambda_points(
        radius=parameters.radius,
        thickness=parameters.thickness,
        gap=0,
    )
    lambda_points_gap = make_lambda_points(
        radius=parameters.radius,
        thickness=parameters.thickness,
        gap=parameters.gap,
    )

    dimension_arrows = make_dimension_arrow_defs()
    construction_lines = make_lambda_construction_lines(parameters=parameters)

    lambda_no_gap = (
        svg.Polygon(
            points=lambda_points.to_list(),
            stroke=parameters.object_lines.stroke,
            stroke_width=parameters.object_lines.stroke_width,
            fill="transparent",
            stroke_dasharray=4,
        ),
    )
    lambda_with_gap = (
        svg.Polygon(
            points=lambda_points_gap.to_list(),
            stroke=parameters.object_lines.stroke,
            stroke_width=parameters.object_lines.stroke_width,
            fill="transparent",
        ),
    )
    dim_main_diagonal = make_dimension_line(
        point1=hexagon_points[1],
        point2=hexagon_points[4],
        side="right",
        offset=1 / 2,
        parameters=parameters,
    )
    dim_lambda_long_edge = make_dimension_line(
        point1=lambda_points[2],
        point2=lambda_points[1],
        side="right",
        offset=7 / 16,
        parameters=parameters,
    )
    dim_gap_diagonal = make_dimension_line(
        point1=(lambda_points_gap[2] + lambda_points_gap[3]) / 2,
        point2=(lambda_points_gap[0] + lambda_points_gap[1]) / 2,
        side="right",
        offset=15 / 32,
        parameters=parameters,
    )
    dim_lambda_left_top = make_dimension_line(
        point1=lambda_points[0],
        point2=lambda_points[8],
        side="left",
        offset=6 / 16,
        parameters=parameters,
    )
    dim_lambda_short_leg_bottom = make_dimension_line(
        point1=lambda_points[6],
        point2=lambda_points[5],
        side="left",
        offset=8 / 16,
        parameters=parameters,
    )
    dim_lambda_legs_inner_left = make_dimension_line(
        point1=lambda_points[4],
        point2=lambda_points[5],
        side="right",
        offset=4 / 16,
        parameters=parameters,
    )
    dim_lambda_head = make_dimension_line(
        point2=lambda_points[0],
        point1=lambda_points[1],
        side="right",
        offset=1 / 2,
        parameters=parameters,
    )

    dim_angle_inner_legs = make_dimension_angle(
        point1=lambda_points[3],
        point2=lambda_points[5],
        reference=lambda_points[4],
        flip=False,
        large=False,
        side="right",
        ratio=1 / 2,
    )

    dim_angle_long_leg_bottom_left = make_dimension_angle(
        point1=lambda_points[2],
        point2=lambda_points[4],
        reference=lambda_points[3],
        flip=True,
        large=False,
        side="left",
        ratio=1 / 2,
    )

    dim_angle_head_left = make_dimension_angle(
        point1=lambda_points[8],
        point2=lambda_points[1],
        reference=lambda_points[0],
        flip=True,
        large=False,
        side="left",
        ratio=1 / 2,
    )

    dim_angle_blah = make_dimension_angle(
        point1=lambda_points[6],
        point2=lambda_points[8],
        reference=lambda_points[7],
        flip=True,
        large=False,
        side="left",
        ratio=1 / 2,
    )

    lambdas = [
        lambda_no_gap,
        lambda_with_gap,
    ]

    dim_lengths = [
        dim_gap_diagonal,
        dim_main_diagonal,
        dim_lambda_long_edge,
        dim_lambda_left_top,
        dim_lambda_legs_inner_left,
        dim_lambda_short_leg_bottom,
        dim_lambda_head,
    ]

    dim_angles = [
        dim_angle_inner_legs,
        dim_angle_long_leg_bottom_left,
        dim_angle_head_left,
        dim_angle_blah,
    ]

    pink_background = svg.Rect(
        x=parameters.image_parameters.min_x,
        y=parameters.image_parameters.min_y,
        width=parameters.image_parameters.width,
        height=parameters.image_parameters.height,
        fill="purple",
        fill_opacity="0.2",
    )

    return svg.SVG(
        viewBox=svg.ViewBoxSpec(
            min_x=parameters.image_parameters.min_x,
            min_y=parameters.image_parameters.min_y,
            width=parameters.image_parameters.width,
            height=parameters.image_parameters.height,
        ),
        elements=[
            dimension_arrows,
            pink_background,  # delete later
        ]
        + construction_lines
        + lambdas
        + dim_lengths
        + dim_angles,
    )


if __name__ == "__main__":
    object_lines = LineGroup("object", "green", 4)
    construction_lines = LineGroup("construction", "blue", 2)
    dimension_lines = LineGroup("dimension", "red", 1)
    image_parameters = ImageParameters()
    parameters = Parameters(
        object_lines,
        construction_lines,
        dimension_lines,
        image_parameters,
    )
    print(draw(parameters))
