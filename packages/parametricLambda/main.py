import math
import statistics
from dataclasses import dataclass

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


def get_length(point1, point2):
    difference = [x - y for x, y in zip(point1, point2)]
    return math.sqrt(math.pow(difference[0], 2) + math.pow(difference[1], 2))


def elementwise_binop(op, *args):
    return [op(*argz) for argz in zip(*args)]


def make_dimension_line(point1, point2, side, text, offset):
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
            marker_start="url(#head)",
            marker_end="url(#head)",
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

    dimension_arrows = svg.Defs(
        elements=[
            svg.Marker(
                id="head",
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

    construction_lines = [
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
        text="1",
        offset=1 / 2,
    )
    dim_lambda_long_edge = make_dimension_line(
        point1=lambda_points[4:6],
        point2=lambda_points[2:4],
        side="right",
        text="9 / 8",
        offset=7 / 16,
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
        text="15 / 16",
        offset=15 / 32,
    )
    dim_lambda_left_top = make_dimension_line(
        point1=lambda_points[0:20],
        point2=lambda_points[16:18],
        side="left",
        text="3 / 8",
        offset=6 / 16,
    )
    dim_lambda_short_leg_bottom = make_dimension_line(
        point1=lambda_points[12:14],
        point2=lambda_points[10:12],
        side="left",
        text="1 / 8",
        offset=8 / 16,
    )
    dim_lambda_legs_inner_left = make_dimension_line(
        point1=lambda_points[8:10],
        point2=lambda_points[10:12],
        side="right",
        text="1 / 4",
        offset=4 / 16,
    )
    dim_lambda_head = make_dimension_line(
        point2=lambda_points[0:2],
        point1=lambda_points[2:4],
        side="right",
        text="1 / 4",
        offset=1 / 2,
    )

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
        + [
            lambda_no_gap,
            lambda_with_gap,
        ]
        + dim_gap_diagonal
        + dim_main_diagonal
        + dim_lambda_long_edge
        + dim_lambda_left_top
        + dim_lambda_legs_inner_left
        + dim_lambda_short_leg_bottom
        + dim_lambda_head,
    )


if __name__ == "__main__":
    print(draw())
    # print(make_hexagon_points(500))
    # print(make_lambda_points(r=500, thickness=0.5, gap=0))
