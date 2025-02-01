import math
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

    gap_vector = [radius * gap * coordinate for coordinate in (cosd(300), sind(300))]

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
    return [coord for point in points for coord in point]


@dataclass
class Parameters:
    radius = 512
    thickness = 1 / 4
    gap = 1 / 8


def draw() -> svg.SVG:
    parameters = Parameters()

    return svg.SVG(
        viewBox=svg.ViewBoxSpec(
            min_x=-600,
            min_y=-600,
            width=1200,
            height=1200,
        ),
        elements=[
            svg.Defs(
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
            ),
            # delete later
            svg.Rect(
                x=-600,
                y=-600,
                width=1200,
                height=1200,
                fill="purple",
                fill_opacity="0.2",
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
            svg.Polygon(
                points=make_lambda_points(
                    radius=parameters.radius,
                    thickness=parameters.thickness,
                    gap=parameters.gap,
                ),
                stroke="green",
                stroke_width=2,
                fill="transparent",
                transform="scale(1, -1)",
            ),
        ],
    )


if __name__ == "__main__":
    print(draw())
    # print(make_hexagon_points(500))
    # print(make_lambda_points(r=500, thickness=0.5, gap=0))
