import math
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import svg

from nixoslogo.colors import ColorStyle
from nixoslogo.logotype import (
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    Character,
    Characters,
    FontLoader,
)
from nixoslogo.logomark import Lambda, SnowFlake
from nixoslogo.svghelpers import ImageParameters


class ClearSpace(Enum):
    NONE = auto()
    MINIMAL = auto()
    RECOMMENDED = auto()


@dataclass(kw_only=True)
class NixosLogo:
    lambda_radius: int = 512
    lambda_thickness: float = 1 / 4
    lambda_gap: float = 1 / 32
    logomark_color_style: ColorStyle = ColorStyle.GRADIENT
    logotype_cap_height: float | None = None
    logotype_color: str = "black"
    logotype_spacings: tuple[int] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING
    logotype_characters: str = "NixOS"
    logotype_transform: svg.Translate | None = None
    image_parameters: ImageParameters | None = None
    clear_space: ClearSpace = ClearSpace.RECOMMENDED
    background_color: str | None = None

    def __post_init__(self):
        self._init_snowflake()
        self._init_capHeight()
        self._init_logotype()
        self._init_image_parameters()

    def _init_snowflake(self):
        self.ilambda = Lambda(
            radius=self.lambda_radius,
            thickness=self.lambda_thickness,
            gap=self.lambda_gap,
        )
        self.logomark = SnowFlake(
            ilambda=self.ilambda,
            color_style=self.logomark_color_style,
        )

    def _init_capHeight(self):
        if self.logotype_cap_height is None:
            self.logotype_cap_height = (
                self.lambda_radius * (1 + self.lambda_thickness * 2) * math.sqrt(3)
            )

    def _init_logotype(self):
        self.loader = FontLoader(capHeight=self.logotype_cap_height)
        self.logotype = Characters(
            characters=[
                Character(
                    character=letter,
                    loader=self.loader,
                    color=self.logotype_color,
                )
                for letter in self.logotype_characters
            ],
            spacings=self.logotype_spacings,
        )

        if self.logotype_transform is None:
            self.logotype_transform = svg.Translate(
                9 / 4 * self.lambda_radius, self.logotype_cap_height / 2
            )

    @property
    def elements_bounding_box(self):
        logomark_box = self.logomark.bounding_box
        logotype_box = self.logotype.boundingBox
        logotype_box_translated = (
            logotype_box[0] + self.logotype_transform.x,
            logotype_box[1] + self.logotype_transform.y,
            logotype_box[2] + self.logotype_transform.x,
            logotype_box[3] + self.logotype_transform.y,
        )
        return [
            predicate(elem)
            for predicate, elem in zip(
                (min, min, max, max),
                list(zip(*(logomark_box, logotype_box_translated))),
            )
        ]

    @property
    def bounding_box(self):
        return (
            self.image_parameters.min_x,
            self.image_parameters.min_y,
            self.image_parameters.min_x + self.image_parameters.width,
            self.image_parameters.min_y + self.image_parameters.height,
        )

    def _init_image_parameters(self):
        if self.image_parameters is None:
            min_x, min_y, max_x, max_y = self.elements_bounding_box

            clear_space = self._get_clearspace()
            min_x -= clear_space
            min_y -= clear_space
            max_x += clear_space
            max_y += clear_space

            width = max_x - min_x
            height = max_y - min_y

            self.image_parameters = ImageParameters(
                min_x=min_x,
                min_y=min_y,
                width=width,
                height=height,
            )

    def _get_clearspace(self):
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.logomark.radius * math.sqrt(3) / 4
            case ClearSpace.RECOMMENDED:
                return self.logomark.radius * math.sqrt(3) / 2
            case _:
                raise Exception("Unknown ClearSpace")

    def make_svg_elements(self):
        background = (
            ()
            if self.background_color is None
            else self.image_parameters.make_svg_background(fill=self.background_color)
        )
        return background + (
            self.logomark.get_svg_elements(),
            svg.G(
                transform=[self.logotype_transform],
                elements=self.logotype.make_svg_elements(),
            ),
        )

    def make_svg(self):
        return svg.SVG(
            viewBox=self.image_parameters.make_view_box(),
            elements=self.make_svg_elements(),
        )

    def write_svg(self):
        with open(Path("test-logo.svg"), "w") as file:
            file.write(str(self.make_svg()))


if __name__ == "__main__":
    NixosLogo(background_color="#dddddd").write_svg()
