import logging
from dataclasses import dataclass
from typing import override

import svg

from nixoslogo.annotations import Annotations
from nixoslogo.core import BaseRenderable, ClearSpace, Shape, flatten_svg_elements
from nixoslogo.logging_config import setup_logging
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Lambda, Logomark
from nixoslogo.logotype import Glyph, Logotype

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class LogoClearspace(BaseRenderable):
    logo: BaseRenderable
    logo_name: str
    space_object: Shape
    annotations: Annotations

    @property
    @override
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        return self.logo.elements_bounding_box

    @property
    @override
    def clearspace_unit(self) -> float:
        return self.logo.clearspace_unit

    @override
    def make_filename(self, extras: tuple[str, ...] = ()) -> str:
        return "-".join(
            [
                "nixos",
                self.logo_name,
                "clearspace",
            ]
            + list(extras)
        )

    @override
    def make_svg_elements(self) -> list[svg.Element]:
        return flatten_svg_elements(
            self.make_greyscale_def(),
            self.make_grid_lines(),
            self.make_clearspace_lines(),
            self.logo.make_svg_elements(),
            self.make_space_object_elements(),
        )

    def make_greyscale_def(self):
        return (
            svg.Defs(
                elements=[
                    svg.Filter(
                        id="greyscale-50",
                        elements=[
                            svg.FeColorMatrix(
                                type="matrix",
                                values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0",
                            ),
                        ],
                    ),
                ],
            ),
        )

    def make_space_object_elements(self):
        transforms: list[list[svg.Transform]] = [
            [
                svg.Rotate(90 * index),
                svg.Translate(
                    -self.space_object.elements_x_min,
                    -self.space_object.elements_y_max,
                ),
                *translation,
            ]
            for index, translation in enumerate(
                (
                    (
                        svg.Translate(
                            +self.logo.elements_x_min,
                            +self.canvas.max_y,
                        ),
                    ),
                    (
                        svg.Translate(
                            +self.logo.elements_y_min,
                            -self.canvas.min_x,
                        ),
                    ),
                    (
                        svg.Translate(
                            -self.logo.elements_x_max,
                            -self.canvas.min_y,
                        ),
                    ),
                    (
                        svg.Translate(
                            -self.logo.elements_y_max,
                            +self.canvas.max_x,
                        ),
                    ),
                )
            )
        ]
        return tuple(
            self.make_space_object_element(
                space=self.space_object,
                transform=transform,
            )
            for transform in transforms
        )

    def make_space_object_element(
        self, space: Shape, transform: list[svg.Transform] | None = None
    ):
        return svg.G(
            elements=(space.make_svg_elements()),
            filter="url(#greyscale-50)",
            transform=transform,
        )

    def make_grid_lines(self):
        return (
            svg.Line(
                x1=self.logo.elements_x_min,
                y1=self.canvas.min_y,
                x2=self.logo.elements_x_min,
                y2=self.canvas.max_y,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.logo.elements_x_max,
                y1=self.canvas.min_y,
                x2=self.logo.elements_x_max,
                y2=self.canvas.max_y,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.canvas.min_x,
                y1=self.logo.elements_y_min,
                x2=self.canvas.max_x,
                y2=self.logo.elements_y_min,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.canvas.min_x,
                y1=self.logo.elements_y_max,
                x2=self.canvas.max_x,
                y2=self.logo.elements_y_max,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
        )

    def make_clearspace_lines(self):
        recommended = self.logo.make_canvas(ClearSpace.RECOMMENDED)
        minimal = self.logo.make_canvas(ClearSpace.MINIMAL)
        recommended_annotation = self.annotations.make_annotation(text="RECOMMENDED")
        minimal_annotation = self.annotations.make_annotation(text="MINIMAL")
        return (
            svg.Rect(
                x=recommended.min_x,
                y=recommended.min_y,
                width=recommended.width,
                height=recommended.height,
                fill="transparent",
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Rect(
                x=minimal.min_x,
                y=minimal.min_y,
                width=minimal.width,
                height=minimal.height,
                fill="transparent",
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.G(
                transform=[
                    svg.Translate(
                        recommended.min_x
                        + recommended_annotation.elements_height * 0.5,
                        recommended.min_y
                        + recommended_annotation.elements_height * 1.5,
                    ),
                ],
                elements=recommended_annotation.make_svg_elements(),
            ),
            svg.G(
                transform=[
                    svg.Translate(
                        minimal.min_x + minimal_annotation.elements_height * 0.5,
                        minimal.min_y + minimal_annotation.elements_height * 1.5,
                    ),
                ],
                elements=minimal_annotation.make_svg_elements(),
            ),
        )


if __name__ == "__main__":
    setup_logging(level=logging.DEBUG)

    annotations = Annotations.medium(
        overrides={"construction_lines": {"stroke": "grey"}}
    )
    space_object = Lambda(gap=0)
    ilc = LogoClearspace(
        logo=Logomark(),
        logo_name="logomark",
        space_object=space_object,
        annotations=annotations,
    )
    ilc.write_svg(filename=ilc.make_filename(extras=("test",)))

    annotations = Annotations.medium(
        overrides={"construction_lines": {"stroke": "grey"}}
    )
    space_object = Glyph(character="N")
    ilc = LogoClearspace(
        logo=Logotype(),
        logo_name="logotype",
        space_object=space_object,
        annotations=annotations,
    )
    ilc.write_svg(filename=ilc.make_filename(extras=("test",)))

    annotations = Annotations.large(
        overrides={"construction_lines": {"stroke": "grey"}}
    )
    space_object = Logomark()
    ilc = LogoClearspace(
        logo=NixosLogo(),
        logo_name="logo",
        space_object=space_object,
        annotations=annotations,
    )
    ilc.write_svg(filename=ilc.make_filename(extras=("test",)))
