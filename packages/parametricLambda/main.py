import fractions
import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Self

import svg
from svg._types import Number


def make_hexagon_points(radius: Number) -> list[Number]:
    angles = [math.radians(angle) for angle in range(0, 360, 60)]
    points = [(radius * math.cos(angle), radius * math.sin(angle)) for angle in angles]
    return [coord for point in points for coord in point]


def make_diagonal_line(radius: Number) -> list[Number]:
    hexagon_points = make_hexagon_points(radius)
    points = [hexagon_points[2:4], hexagon_points[8:10]]
    return [coord for point in points for coord in point]


def cosd(angle) -> float:
    return math.cos(math.radians(angle))


def sind(angle) -> float:
    return math.sin(math.radians(angle))


def get_normal(point1, point2):
    normal = (
        -(point2[1] - point1[1]),
        point2[0] - point1[0],
    )
    modulus = math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2))
    return [coordinate / modulus for coordinate in normal]


def get_normalized(point1, point2):
    difference = [y - x for x, y in zip(point1, point2)]
    modulus = math.sqrt(math.pow(difference[0], 2) + math.pow(difference[1], 2))
    return [coordinate / modulus for coordinate in difference]


def get_length(point1, point2):
    difference = [x - y for x, y in zip(point1, point2)]
    return math.sqrt(math.pow(difference[0], 2) + math.pow(difference[1], 2))


def get_vector_length(vector):
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))


def get_vector_normalized(vector):
    modulus = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))
    return [coordinate / modulus for coordinate in vector]


def get_dot_product(vector1, vector2):
    return sum([x * y for x, y in zip(vector1, vector2)])


def get_angle(vector1, vector2):
    return math.degrees(
        math.acos(
            get_dot_product(vector1, vector2)
            / (get_vector_length(vector1) * get_vector_length(vector2))
        )
    )


def elementwise_binop(op, *args):
    return [op(*argz) for argz in zip(*args)]


@dataclass
class Point:
    x: Number
    y: Number

    def __add__(self, other: Self) -> Self:
        return Point(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return Vector((self.x - other.x, self.y - other.y))

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


def make_dimension_line(point1, point2, side, offset, parameters, text=None):
    normal = get_normal(point1, point2)
    distance = offset * get_length(point1, point2)

    point1_end = [elem + 1.25 * distance * norm for elem, norm in zip(point1, normal)]
    point2_end = [elem + 1.25 * distance * norm for elem, norm in zip(point2, normal)]
    point1_dim = [elem + 1.20 * distance * norm for elem, norm in zip(point1, normal)]
    point2_dim = [elem + 1.20 * distance * norm for elem, norm in zip(point2, normal)]

    text_offset = 1.19 if side == "left" else 1.21
    point1_text = [
        elem + text_offset * distance * norm for elem, norm in zip(point1, normal)
    ]
    point2_text = [
        elem + text_offset * distance * norm for elem, norm in zip(point2, normal)
    ]

    input_hash = hash((tuple(point1), tuple(point2), side, text, offset))

    if text is None:
        text = fractions.Fraction(
            round(get_length(point1, point2)), 2 * parameters.radius
        )

    return [
        svg.Line(
            x1=point1[0],
            y1=point1[1],
            x2=point1_end[0],
            y2=point1_end[1],
            stroke="red",
        ),
        svg.Line(
            x1=point2[0],
            y1=point2[1],
            x2=point2_end[0],
            y2=point2_end[1],
            stroke="red",
        ),
        svg.Line(
            x1=point1_dim[0],
            y1=point1_dim[1],
            x2=point2_dim[0],
            y2=point2_dim[1],
            stroke="red",
            marker_start="url(#dimension-arrow-head)",
            marker_end="url(#dimension-arrow-head)",
        ),
        svg.Path(
            id=f"dimension_path_{input_hash}",
            d=[svg.M(*point1_text), svg.L(*point2_text)],
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


def make_dimension_angle(points, flip, large, side, ratio, text=None):
    points = points if not flip else points[4:] + points[2:4] + points[:2]

    reference = points[2:4]
    vector1 = [point - reference for point, reference in zip(points[:2], reference)]
    vector2 = [point - reference for point, reference in zip(points[4:], reference)]

    length1 = get_vector_length(vector1)
    length2 = get_vector_length(vector2)
    shorter_length = min(length1, length2)

    mid_point_1 = [
        reference + vector * shorter_length * ratio
        for reference, vector in zip(reference, get_vector_normalized(vector1))
    ]
    mid_point_2 = [
        reference + vector * shorter_length * ratio
        for reference, vector in zip(reference, get_vector_normalized(vector2))
    ]

    arc_radius = min(length1 / 2, length2 / 2)

    input_hash = hash((tuple(points), flip, large, text, side, ratio))

    if text is None:
        text = f"{round(get_angle(vector1, vector2))}°"

    return [
        svg.Path(
            id=f"dimension_angle_{input_hash}",
            d=[
                svg.M(*mid_point_1),
                svg.Arc(
                    arc_radius,
                    arc_radius,
                    0,
                    large,
                    True,
                    *mid_point_2,
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
    hex_top_left = hexagon_points[4:6]
    hex_bottom_left = hexagon_points[8:10]
    hex_bottom_right = hexagon_points[10:12]

    vector_0 = [radius * thickness * coordinate for coordinate in (cosd(0), sind(0))]
    vector_60 = [radius * thickness * coordinate for coordinate in (cosd(60), sind(60))]
    vector_270 = [
        radius * thickness * coordinate for coordinate in (cosd(270), sind(270))
    ]
    vector_300 = [
        radius * thickness * coordinate for coordinate in (cosd(300), sind(300))
    ]

    gap_vector = [
        2 * radius * gap * coordinate for coordinate in (cosd(300), sind(300))
    ]

    points = [
        (x - y + z for x, y, z in zip(hex_top_left, vector_60, gap_vector)),
        (x + y + z for x, y, z in zip(hex_top_left, vector_60, gap_vector)),
        (x + y for x, y in zip(hex_bottom_right, vector_0)),
        (x - y for x, y in zip(hex_bottom_right, vector_0)),
        (x * math.sqrt(3) for x in vector_270),
        (x + y for x, y in zip(hex_bottom_left, vector_0)),
        hex_bottom_left,
        (x - y for x, y in zip(hex_bottom_left, vector_300)),
        (-x for x in vector_0),
    ]
    points = [(x, -y) for x, y in points]
    return [coord for point in points for coord in point]


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
            x1=-10 * parameters.radius,
            x2=10 * parameters.radius,
            y1=0,
            y2=0,
            stroke="black",
        ),
        svg.Line(
            x1=0,
            x2=0,
            y1=-10 * parameters.radius,
            y2=10 * parameters.radius,
            stroke="black",
        ),
        svg.Circle(
            cx=0,
            cy=0,
            r=parameters.radius,
            stroke="blue",
            stroke_width=1,
            stroke_dasharray=4,
            fill="transparent",
        ),
        svg.Polygon(
            points=make_hexagon_points(radius=parameters.radius),
            stroke="blue",
            stroke_width=1,
            stroke_dasharray=4,
            fill="transparent",
        ),
        svg.Polyline(
            points=make_diagonal_line(radius=parameters.radius),
            stroke="blue",
            stroke_width=1,
            stroke_dasharray=4,
            fill="transparent",
        ),
    ]


@dataclass
class Parameters:
    radius = 512
    thickness = 1 / 4
    gap = 1 / 16


def draw() -> svg.SVG:
    parameters = Parameters()
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
            points=make_lambda_points(
                radius=parameters.radius,
                thickness=parameters.thickness,
                gap=0,
            ),
            stroke="green",
            stroke_width=2,
            fill="transparent",
            # transform="scale(1, -1)",
            stroke_dasharray=4,
        ),
    )
    lambda_with_gap = (
        svg.Polygon(
            points=make_lambda_points(
                radius=parameters.radius,
                thickness=parameters.thickness,
                gap=parameters.gap,
            ),
            stroke="green",
            stroke_width=2,
            fill="transparent",
            # transform="scale(1, -1)",
        ),
    )
    dim_main_diagonal = make_dimension_line(
        point1=hexagon_points[2:4],
        point2=hexagon_points[8:10],
        side="right",
        offset=1 / 2,
        parameters=parameters,
    )
    dim_lambda_long_edge = make_dimension_line(
        point1=lambda_points[4:6],
        point2=lambda_points[2:4],
        side="right",
        offset=7 / 16,
        parameters=parameters,
    )
    dim_gap_diagonal = make_dimension_line(
        point1=[
            statistics.mean(args)
            for args in zip(lambda_points_gap[4:6], lambda_points_gap[6:8])
        ],
        point2=[
            statistics.mean(args)
            for args in zip(lambda_points_gap[0:2], lambda_points_gap[2:4])
        ],
        side="right",
        offset=15 / 32,
        parameters=parameters,
    )
    dim_lambda_left_top = make_dimension_line(
        point1=lambda_points[0:2],
        point2=lambda_points[16:18],
        side="left",
        offset=6 / 16,
        parameters=parameters,
    )
    dim_lambda_short_leg_bottom = make_dimension_line(
        point1=lambda_points[12:14],
        point2=lambda_points[10:12],
        side="left",
        offset=8 / 16,
        parameters=parameters,
    )
    dim_lambda_legs_inner_left = make_dimension_line(
        point1=lambda_points[8:10],
        point2=lambda_points[10:12],
        side="right",
        offset=4 / 16,
        parameters=parameters,
    )
    dim_lambda_head = make_dimension_line(
        point2=lambda_points[0:2],
        point1=lambda_points[2:4],
        side="right",
        offset=1 / 2,
        parameters=parameters,
    )

    dim_angle_inner_legs = make_dimension_angle(
        points=lambda_points[6:12],
        flip=False,
        large=False,
        side="right",
        ratio=1 / 2,
    )

    dim_angle_long_leg_bottom_left = make_dimension_angle(
        points=lambda_points[4:10],
        flip=True,
        large=False,
        side="left",
        ratio=1 / 2,
    )

    dim_angle_head_left = make_dimension_angle(
        points=lambda_points_gap[16:] + lambda_points_gap[:4],
        flip=True,
        large=False,
        side="left",
        ratio=1 / 2,
    )

    dim_angle_blah = make_dimension_angle(
        points=lambda_points[12:18],
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
        x=-900,
        y=-1100,
        width=2100,
        height=1900,
        fill="purple",
        fill_opacity="0.2",
    )

    return svg.SVG(
        viewBox=svg.ViewBoxSpec(
            min_x=-900,
            min_y=-1100,
            width=2100,
            height=1900,
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
    # print(draw())

    p1 = Point(1, 2)
    p2 = Point(3, 4)

    print((p2 + p1).distance(p2))
    print(p2 - p1)
    print(p1 - p2)

    v1 = -(p1 - p2)
    print(v1)
    print(v1.length())
    print(v1.dot(v1))
    print(v1.normalize())
    print(Vector((1, 2)))
    print(p1.normal(p2))
    print(v1.normal())
    print(3 * v1)
    print(str(v1))
    print(repr(v1))

    # print(make_hexagon_points(500))
    # print(make_lambda_points(r=500, thickness=0.5, gap=0))
