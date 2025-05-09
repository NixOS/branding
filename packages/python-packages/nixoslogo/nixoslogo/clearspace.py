import logging

import svg

from nixoslogo.annotations import Annotations
from nixoslogo.core import BaseRenderable, ClearSpace
from nixoslogo.logging_config import setup_logging
from nixoslogo.logo import Lambda, NixosLogo
from nixoslogo.logomark import Logomark
from nixoslogo.logotype import Glyph, Logotype

logger = logging.getLogger(__name__)


class LogomarkDimensionedClearspace(BaseRenderable):
    def __init__(
        self,
        logo: BaseRenderable,
        space_object: BaseRenderable,
        annotations: Annotations,
        **kwargs,
    ):
        self.logo = logo
        self.space_object = space_object
        self.annotations = annotations

        self.recommended = self.logo(clear_space=ClearSpace.RECOMMENDED)
        self.minimal = self.logo(clear_space=ClearSpace.MINIMAL)
        super().__init__(**kwargs)

    @property
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        return self.recommended.elements_bounding_box

    def _get_clearspace(self) -> float:
        return self.recommended._get_clearspace()

    def make_filename(self, extras: tuple[str] = ()) -> str:
        return self.recommended.make_filename(extras=extras)

    def make_svg_elements(self):
        return (
            self.make_greyscale_def(),
            self.make_grid_lines(),
            self.make_clearspace_lines(),
            self.recommended.make_svg_elements(),
            self.make_space_object_elements(),
        )

    def make_greyscale_def(self):
        return (
            svg.Defs(
                elements=(
                    svg.Filter(
                        id="greyscale-50",
                        elements=(
                            svg.FeColorMatrix(
                                type="matrix",
                                values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0",
                            ),
                        ),
                    ),
                ),
            ),
        )

    def make_space_object_elements(self):
        transforms = [
            (
                svg.Rotate(90 * index),
                svg.Translate(
                    -self.space_object.elements_x_min,
                    -self.space_object.elements_y_max,
                ),
                translation,
            )
            for index, translation in enumerate(
                (
                    (
                        svg.Translate(
                            +self.recommended.elements_x_min,
                            +self.canvas.max_y,
                        ),
                    ),
                    (
                        svg.Translate(
                            +self.recommended.elements_y_min,
                            -self.canvas.min_x,
                        ),
                    ),
                    (
                        svg.Translate(
                            -self.recommended.elements_x_max,
                            -self.canvas.min_y,
                        ),
                    ),
                    (
                        svg.Translate(
                            -self.recommended.elements_y_max,
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

    def make_space_object_element(self, space, transform=None):
        return svg.G(
            elements=(space.make_svg_elements()),
            filter="url(#greyscale-50)",
            transform=transform,
        )

    def make_grid_lines(self):
        return (
            svg.Line(
                x1=self.recommended.elements_x_min,
                y1=self.canvas.min_y,
                x2=self.recommended.elements_x_min,
                y2=self.canvas.max_y,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.recommended.elements_x_max,
                y1=self.canvas.min_y,
                x2=self.recommended.elements_x_max,
                y2=self.canvas.max_y,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.canvas.min_x,
                y1=self.recommended.elements_y_min,
                x2=self.canvas.max_x,
                y2=self.recommended.elements_y_min,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Line(
                x1=self.canvas.min_x,
                y1=self.recommended.elements_y_max,
                x2=self.canvas.max_x,
                y2=self.recommended.elements_y_max,
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
        )

    def make_clearspace_lines(self):
        recommended_annotation = self.annotations.make_annotation(text="RECOMMENDED")
        minimal_annotation = self.annotations.make_annotation(text="MINIMAL")
        return (
            svg.Rect(
                x=self.recommended.canvas.min_x,
                y=self.recommended.canvas.min_y,
                width=self.recommended.canvas.width,
                height=self.recommended.canvas.height,
                fill="transparent",
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.Rect(
                x=self.minimal.canvas.min_x,
                y=self.minimal.canvas.min_y,
                width=self.minimal.canvas.width,
                height=self.minimal.canvas.height,
                fill="transparent",
                stroke=self.annotations.construction_lines.stroke,
                stroke_width=self.annotations.construction_lines.stroke_width,
                stroke_dasharray=self.annotations.construction_lines.stroke_dasharray,
            ),
            svg.G(
                transform=(
                    svg.Translate(
                        self.recommended.canvas.min_x
                        + recommended_annotation.elements_height * 0.5,
                        self.recommended.canvas.min_y
                        + recommended_annotation.elements_height * 1.5,
                    ),
                ),
                elements=recommended_annotation.make_svg_elements(),
            ),
            svg.G(
                transform=(
                    svg.Translate(
                        self.minimal.canvas.min_x
                        + minimal_annotation.elements_height * 0.5,
                        self.minimal.canvas.min_y
                        + minimal_annotation.elements_height * 1.5,
                    ),
                ),
                elements=minimal_annotation.make_svg_elements(),
            ),
        )


if __name__ == "__main__":
    setup_logging(level=logging.DEBUG)

    annotations = Annotations.medium()
    annotations.construction_lines.stroke = "grey"
    # annotations.construction_lines.stroke_dasharray = 32

    space_object = Lambda(gap=0)
    original = LogomarkDimensionedClearspace(
        logo=Logomark,
        space_object=space_object,
        annotations=annotations,
    )
    original.write_svg()

    space_object = Glyph(character="N")
    original = LogomarkDimensionedClearspace(
        logo=Logotype,
        space_object=space_object,
        annotations=annotations,
    )
    original.write_svg()

    annotations = Annotations.large()
    annotations.construction_lines.stroke = "grey"
    space_object = Logomark()
    original = LogomarkDimensionedClearspace(
        logo=NixosLogo,
        space_object=space_object,
        annotations=annotations,
    )
    original.write_svg()
