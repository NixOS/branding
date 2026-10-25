import fractions
import math
from dataclasses import dataclass, field, replace
from typing import Self, TypedDict, override

import svg
from svg._types import Number

from nixoslogo.core import (
    CHARACTER_GLYPHNAME_MAP,
    DEFAULT_JURA_TRANSFORMS,
    BaseRenderable,
    flatten_svg_elements,
    get_nixos_annotation_font_file,
)
from nixoslogo.geometry import Point
from nixoslogo.helpers import arc_sagitta
from nixoslogo.logotype import FontLoader, Glyph


@dataclass(kw_only=True)
class TextAnnotations(BaseRenderable):
    characters: str
    loader: FontLoader
    color: str = "black"
    cap_height: float | None = None
    glyphs: tuple[Glyph, ...] = field(init=False)
    original_cap_height: float = field(init=False)

    def __post_init__(self) -> None:
        self._load_glyphs()
        self.original_cap_height = self.loader.capHeight
        self._set_spacings()
        self._scale_glyphs()

    def _map_characters(self, character: str) -> str:
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
    @override
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
        if self.cap_height is None:
            return
        scale = self.original_cap_height / self.cap_height
        for glyph in self.glyphs:
            glyph.layer.transform((1 / scale, 0, 0, 1 / scale, 0, 0))

    @property
    @override
    def clearspace_unit(self) -> float:
        return 0

    @override
    def make_svg_elements(self) -> list[svg.Element]:
        return flatten_svg_elements(*(elem.make_svg_element() for elem in self.glyphs))

    @override
    def make_filename(self, extras: tuple[str, ...] = ()):
        return "-".join(
            [
                self.characters.lower(),
                "annotation",
                self.color,
            ]
            + list(extras)
        )


@dataclass(frozen=True, kw_only=True)
class LineGroup:
    name: str
    stroke: str
    stroke_width: int
    stroke_dasharray: list[Number]
    fill: str = "transparent"


class LineGroupOverrides(TypedDict, total=False):
    stroke: str
    stroke_width: int
    stroke_dasharray: list[Number]
    fill: str


class DimensionLinesOverrides(LineGroupOverrides, total=False):
    font_loader: FontLoader
    cap_height: float
    color: str


class AnnotationsOverrides(TypedDict, total=False):
    object_lines: LineGroupOverrides
    construction_lines: LineGroupOverrides
    dimension_lines: DimensionLinesOverrides


@dataclass(frozen=True, kw_only=True)
class DimensionLines(LineGroup):
    font_loader: FontLoader
    cap_height: float
    color: str

    def make_annotation(self, text: str) -> TextAnnotations:
        return TextAnnotations(
            characters=text,
            loader=self.font_loader,
            cap_height=self.cap_height,
            color=self.color,
        )

    def make_dimension_line(
        self,
        point1: Point,
        point2: Point,
        flip: bool = False,
        side: str = "left",
        offset: float = 1,
        reference: float = 1,
        text: str | None = None,
        text_offset: bool = False,
        fractional: bool = True,
        precision: int = 3,
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
                    label = fractions.Fraction(
                        round(measured_line.length()), round(reference)
                    )
                else:
                    label = round(measured_line.length() / reference, precision)
            else:
                label = text

            text_annotation = self.make_annotation(str(label))
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
        point1: Point,
        point2: Point,
        flip: bool = False,
        side: str = "left",
        offset: float = 1,
        reference: float = 1,
        text: str | None = None,
        text_offset: bool = False,
        fractional: bool = True,
        precision: int = 3,
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
                    label = fractions.Fraction(
                        round(measured_line.length()), round(reference)
                    )
                else:
                    label = round(measured_line.length() / reference, precision)
            else:
                label = text

            text_annotation = self.make_annotation(str(label))
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
        point1: Point,
        point2: Point,
        reference: Point,
        flip: bool,
        large: bool,
        ratio: float,
        text: str | None = None,
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

        text_annotation = self.make_annotation(str(text))
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


@dataclass(frozen=True, kw_only=True)
class Annotations:
    object_lines: LineGroup
    construction_lines: LineGroup
    dimension_lines: DimensionLines

    def make_annotation(self, text: str) -> TextAnnotations:
        return self.dimension_lines.make_annotation(text)

    @classmethod
    def sized(
        cls, multiplier: int, overrides: AnnotationsOverrides | None = None
    ) -> Self:
        base = cls(
            object_lines=LineGroup(
                name="object",
                stroke="green",
                stroke_width=4 * multiplier,
                stroke_dasharray=[4 * multiplier],
            ),
            construction_lines=LineGroup(
                name="construction",
                stroke="blue",
                stroke_width=2 * multiplier,
                stroke_dasharray=[4 * multiplier],
            ),
            dimension_lines=DimensionLines(
                name="dimension",
                stroke="red",
                stroke_width=1 * multiplier,
                stroke_dasharray=[4 * multiplier],
                font_loader=FontLoader(
                    get_font_file=get_nixos_annotation_font_file,
                    transforms_map=DEFAULT_JURA_TRANSFORMS,
                    offset_glyph=False,
                ),
                cap_height=24 * multiplier,
                color="black",
            ),
        )
        if overrides is None:
            return base
        return replace(
            base,
            object_lines=replace(
                base.object_lines, **overrides.get("object_lines", {})
            ),
            construction_lines=replace(
                base.construction_lines, **overrides.get("construction_lines", {})
            ),
            dimension_lines=replace(
                base.dimension_lines, **overrides.get("dimension_lines", {})
            ),
        )

    @classmethod
    def small(cls, overrides: AnnotationsOverrides | None = None) -> Self:
        return cls.sized(1, overrides)

    @classmethod
    def medium(cls, overrides: AnnotationsOverrides | None = None) -> Self:
        return cls.sized(2, overrides)

    @classmethod
    def large(cls, overrides: AnnotationsOverrides | None = None) -> Self:
        return cls.sized(4, overrides)


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
