import fractions
import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import svg

from nixoslogo.core import (
    CHARACTER_GLYPHNAME_MAP,
    DEFAULT_JURA_TRANSFORMS,
    BaseRenderable,
    get_nixos_annotation_font_file,
)
from nixoslogo.geometry import Point
from nixoslogo.helpers import arc_sagitta
from nixoslogo.logotype import FontLoader, Glyph


class TextAnnotations(BaseRenderable):
    def __init__(
        self,
        characters: str,
        loader: FontLoader,
        color: str = "black",
        scale: float | None = None,
        cap_height: float | None = None,
        **kwargs,
    ):
        self.characters = characters
        self.loader = loader
        self.color = color
        self.scale = scale
        self.cap_height = cap_height

        self._load_glyphs()
        self.original_cap_height = self.loader.capHeight
        self.original_scale = self.loader.scale
        self._set_spacings()
        self._scale_glyphs()

        super().__init__(**kwargs)

    def _map_characters(self, character):
        return CHARACTER_GLYPHNAME_MAP.get(character, character)

    def _load_glyphs(self):
        self.glyphs = tuple(
            Glyph(
                loader=self.loader,
                character=self._map_characters(character),
                color=self.color,
            )
            for character in self.characters
        )

    @property
    def elements_bounding_box(self):
        characters_box = tuple(
            f(elem)
            for f, elem in zip(
                (min, min, max, max),
                list(zip(*(elem.elements_bounding_box for elem in self.glyphs))),
            )
        )
        return characters_box

    def _set_spacings(self):
        x_offset = 0
        first = True
        for glyph in self.glyphs:
            if first:
                first = False
                x_offset -= glyph.glyph.left_side_bearing

            glyph.layer.transform((1, 0, 0, 1, x_offset, 0))
            x_offset += glyph.glyph.width

    def _scale_glyphs(self):
        if self.scale is None and self.cap_height is None:
            return

        if self.scale is not None and self.cap_height is not None:
            raise ValueError("Only one of scale or cap_height can be set.")

        if self.cap_height is not None:
            self.scale = self.original_cap_height / self.cap_height
        else:
            self.cap_height = self.original_cap_height / self.scale

        for glyph in self.glyphs:
            glyph.layer.transform((1 / self.scale, 0, 0, 1 / self.scale, 0, 0))

    def _get_clearspace(self):
        return 0

    def make_svg_elements(self):
        return tuple(elem.make_svg_element() for elem in self.glyphs)

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                self.characters.lower(),
                "annotation",
                self.color,
            ]
            + list(extras)
        )


@dataclass
class LineGroup:
    name: str
    stroke: str
    stroke_width: int
    stroke_dasharray: int
    fill: str = "transparent"


class ObjectLines(LineGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ConstructionLines(LineGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DimensionLines(LineGroup):
    def __init__(
        self,
        font_loader: FontLoader,
        font_config: dict,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.font_loader = font_loader
        self.font_config = font_config

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

        if text == "":
            text_element = ()
        else:
            if text is None:
                if fractional:
                    text = fractions.Fraction(round(measured_line.length()), reference)
                else:
                    text = round(measured_line.length() / reference, precision)

            text_annotation = TextAnnotations(
                characters=str(text),
                loader=self.font_loader,
                **self.font_config,
            )
            annotation_center = Point(
                (
                    text_annotation.elements_width / 2,
                    -text_annotation.elements_height / 2,
                )
            )

            # TODO @djacu simplify transforms
            if text_offset:
                translate_to = (point1_end + point2_end) / 2
                text_element = (
                    svg.G(
                        transform=[
                            svg.Translate(*(-annotation_center)),
                            svg.Translate(*translate_to),
                            svg.Translate(0, -annotation_center.y * 3 / 2),
                        ],
                        elements=(text_annotation.make_svg_elements()),
                    ),
                )
            else:
                translate_to = (point1_dim + point2_dim) / 2
                text_element = (
                    svg.G(
                        transform=[
                            svg.Translate(*(-annotation_center)),
                            svg.Translate(*translate_to),
                            svg.Rotate(
                                -math.degrees(
                                    math.atan2(*(point2_dim - point1_dim).normal())
                                ),
                                *annotation_center,
                            ),
                            svg.Rotate(
                                180 if side == "left" else 0, *annotation_center
                            ),
                            svg.Translate(0, annotation_center.y * 5 / 4),
                        ],
                        elements=(text_annotation.make_svg_elements()),
                    ),
                )

        return (
            svg.Line(
                x1=point1.x,
                y1=point1.y,
                x2=point1_end.x,
                y2=point1_end.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
            ),
            svg.Line(
                x1=point2.x,
                y1=point2.y,
                x2=point2_end.x,
                y2=point2_end.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
            ),
            svg.Line(
                x1=point1_dim.x,
                y1=point1_dim.y,
                x2=point2_dim.x,
                y2=point2_dim.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
                marker_start="url(#dimension-arrow-head)",
                marker_end="url(#dimension-arrow-head)",
            ),
            svg.Path(  # TODO @djacu get rid of this; it was used for text elements on path
                d=[
                    svg.M(point1_text.x, point1_text.y),
                    svg.L(point2_text.x, point2_text.y),
                ],
            ),
            text_element,
        )

    def make_dimension_line_outer(
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
        point1_dim_tail = (
            point1_dim
            + max(40, measured_line.length() / 10) * measured_line.normalize()
        )
        point2_dim_tail = (
            point2_dim
            - max(40, measured_line.length() / 10) * measured_line.normalize()
        )

        if text == "":
            text_element = ()
        else:
            if text is None:
                if fractional:
                    text = fractions.Fraction(round(measured_line.length()), reference)
                else:
                    text = round(measured_line.length() / reference, precision)

            text_annotation = TextAnnotations(
                characters=str(text),
                loader=self.font_loader,
                **self.font_config,
            )
            annotation_center = Point(
                (
                    text_annotation.elements_width / 2,
                    -text_annotation.elements_height / 2,
                )
            )

            if text_offset:
                translate_to = (
                    point1_dim_tail
                    + (
                        text_annotation.elements_width / 2
                        + text_annotation.elements_height / 2
                    )
                    * measured_line.normalize()
                )
            else:
                translate_to = (point1_dim + point2_dim) / 2

            text_element = (
                svg.G(
                    transform=[
                        svg.Translate(*(-annotation_center)),
                        svg.Translate(*translate_to),
                        svg.Rotate(
                            -math.degrees(
                                math.atan2(*(point2_dim - point1_dim).normal())
                            ),
                            *annotation_center,
                        ),
                        svg.Rotate(180 if side == "left" else 0, *annotation_center),
                    ],
                    elements=(text_annotation.make_svg_elements()),
                ),
            )

        return (
            # side line
            svg.Line(
                x1=point1.x,
                y1=point1.y,
                x2=point1_end.x,
                y2=point1_end.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
            ),
            # side line
            svg.Line(
                x1=point2.x,
                y1=point2.y,
                x2=point2_end.x,
                y2=point2_end.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
            ),
            # dimension line
            svg.Line(
                x1=point1_dim.x,
                y1=point1_dim.y,
                x2=point1_dim_tail.x,
                y2=point1_dim_tail.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
                marker_start="url(#dimension-arrow-head)",
            ),
            # dimension line
            svg.Line(
                x1=point2_dim.x,
                y1=point2_dim.y,
                x2=point2_dim_tail.x,
                y2=point2_dim_tail.y,
                stroke=self.stroke,
                stroke_width=self.stroke_width,
                marker_start="url(#dimension-arrow-head)",
            ),
            text_element,
        )

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

        sweep = True

        arc_midpoint, arc_midpoint_vector = arc_sagitta(
            mid_point_1,
            mid_point_2,
            arc_radius,
            large,
            sweep,
        )

        text_annotation = TextAnnotations(
            characters=str(text),
            loader=self.font_loader,
            **self.font_config,
        )
        annotation_center = Point(
            (text_annotation.elements_width / 2, -text_annotation.elements_height / 2)
        )
        annotation_offset = (
            annotation_center.to_vector().length() * 3 / 2 * arc_midpoint_vector
        )

        # TODO @djacu simplify transforms
        return (
            svg.Path(
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
                        sweep,
                        mid_point_2.x,
                        mid_point_2.y,
                    ),
                ],
                stroke=self.stroke,
                stroke_width=self.stroke_width,
                fill=self.fill,
                marker_start="url(#dimension-arrow-head)",
                marker_end="url(#dimension-arrow-head)",
            ),
            svg.G(
                transform=[
                    svg.Translate(*(-annotation_center)),
                    svg.Translate(*arc_midpoint),
                    svg.Translate(*annotation_offset),
                ],
                elements=(text_annotation.make_svg_elements()),
            ),
        )

    def make_dimension_arrow_defs(self):
        return (
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
                                fill=self.stroke,  # can't use fill because of arcs
                            )
                        ],
                    )
                ]
            ),
        )


class Annotations:
    def __init__(
        self,
        object_lines_config: dict,
        construction_lines_config: dict,
        dimension_lines_config: dict,
        font_config: dict,
        get_font_file: Callable[[], Path] = get_nixos_annotation_font_file,
        transforms_map: dict = DEFAULT_JURA_TRANSFORMS,
    ):
        self.font_loader = FontLoader(
            get_font_file=get_font_file,
            transforms_map=transforms_map,
            offset_glyph=False,
        )
        self.font_config = font_config
        self.object_lines = ObjectLines(**object_lines_config)
        self.construction_lines = ConstructionLines(**construction_lines_config)
        self.dimension_lines = DimensionLines(
            **dimension_lines_config,
            font_loader=self.font_loader,
            font_config=self.font_config,
        )

    def make_annotation(self, text):
        return TextAnnotations(
            characters=str(text),
            loader=self.font_loader,
            **self.font_config,
        )

    @classmethod
    def small(cls) -> "Annotations":
        return cls(
            object_lines_config={
                "name": "object",
                "stroke": "green",
                "stroke_width": 4,
                "stroke_dasharray": 4,
            },
            construction_lines_config={
                "name": "construction",
                "stroke": "blue",
                "stroke_width": 2,
                "stroke_dasharray": 4,
            },
            dimension_lines_config={
                "name": "dimension",
                "stroke": "red",
                "stroke_width": 1,
                "stroke_dasharray": 4,
            },
            font_config={
                "scale": None,
                "cap_height": 24,
                "color": "black",
                "stroke_dasharray": 4,
            },
        )

    @classmethod
    def medium(cls) -> "Annotations":
        return cls(
            object_lines_config={
                "name": "object",
                "stroke": "green",
                "stroke_width": 8,
                "stroke_dasharray": 8,
            },
            construction_lines_config={
                "name": "construction",
                "stroke": "blue",
                "stroke_width": 4,
                "stroke_dasharray": 8,
            },
            dimension_lines_config={
                "name": "dimension",
                "stroke": "red",
                "stroke_width": 2,
                "stroke_dasharray": 8,
            },
            font_config={
                "scale": None,
                "cap_height": 48,
                "color": "black",
                "stroke_dasharray": 8,
            },
        )

    @classmethod
    def large(cls) -> "Annotations":
        return cls(
            object_lines_config={
                "name": "object",
                "stroke": "green",
                "stroke_width": 16,
                "stroke_dasharray": 16,
            },
            construction_lines_config={
                "name": "construction",
                "stroke": "blue",
                "stroke_width": 8,
                "stroke_dasharray": 16,
            },
            dimension_lines_config={
                "name": "dimension",
                "stroke": "red",
                "stroke_width": 4,
                "stroke_dasharray": 16,
            },
            font_config={
                "scale": None,
                "cap_height": 96,
                "color": "black",
                "stroke_dasharray": 16,
            },
        )


if __name__ == "__main__":
    from nixoslogo.core import get_nixos_annotation_font_file

    loader = FontLoader(
        get_font_file=get_nixos_annotation_font_file,
        transforms_map=DEFAULT_JURA_TRANSFORMS,
        offset_glyph=False,
    )
    ta = TextAnnotations(
        loader=loader,
        characters="NixOS Logo 9 / 4",
        background_color="#dddddd",
    )
    ta.write_svg()
