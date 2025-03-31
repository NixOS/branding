import fractions
import math
from dataclasses import dataclass

import svg

from .helpers import stable_hash


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
        text_offset=False,
        fractional=True,
        precision=3,
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

        text_offset_scale = 1.19 if side == "left" else 1.21
        point1_text = point1 + text_offset_scale * distance * normal
        point2_text = point2 + text_offset_scale * distance * normal

        if text is None:
            if fractional:
                text = fractions.Fraction(round(measured_line.length()), reference)
            else:
                text = round(measured_line.length() / reference, precision)

        hash_args = locals()
        hash_args.pop("self")
        input_hash = stable_hash(hash_args)

        if not text_offset:
            text_element = (
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
            )
        else:
            text_element = svg.Text(
                font_size=self.dimension_lines.font_size,
                x=(point1_end.x + point2_end.x) / 2,
                y=point2_end.y,
                elements=[text],
                dominant_baseline="alphabetic" if flip else "hanging",
                text_anchor="middle",
            )

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
            text_element,
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

        if text is None:
            text = f"{round(math.degrees(vector1.angle_from(vector2)))}°"

        hash_args = locals()
        hash_args.pop("self")
        input_hash = stable_hash(hash_args)

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
