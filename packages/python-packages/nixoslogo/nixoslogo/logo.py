import math
from pathlib import Path

import svg

from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    BaseRenderable,
    ClearSpace,
    ColorStyle,
)
from nixoslogo.logomark import Lambda, Logomark
from nixoslogo.logotype import (
    Character,
    FontLoader,
    Logotype,
)


class NixosLogo(BaseRenderable):
    def __init__(
        self,
        lambda_radius: int = 512,
        lambda_thickness: float = 1 / 4,
        lambda_gap: float = 1 / 32,
        logomark_color_style: ColorStyle = ColorStyle.GRADIENT,
        logotype_cap_height: float | None = None,
        logotype_color: str = "black",
        logotype_spacings: tuple[int] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
        logotype_characters: str = "NixOS",
        logotype_transform: svg.Translate | None = None,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        **kwargs,
    ):
        self.lambda_radius = lambda_radius
        self.lambda_thickness = lambda_thickness
        self.lambda_gap = lambda_gap
        self.logomark_color_style = logomark_color_style
        self.logotype_cap_height = logotype_cap_height
        self.logotype_color = logotype_color
        self.logotype_spacings = logotype_spacings
        self.logotype_characters = logotype_characters
        self.logotype_transform = logotype_transform
        self.clear_space = clear_space

        self._init_snowflake()
        self._init_cap_height()
        self._init_logotype()

        super().__init__(**kwargs)

    def _init_snowflake(self):
        self.ilambda = Lambda(
            radius=self.lambda_radius,
            thickness=self.lambda_thickness,
            gap=self.lambda_gap,
        )
        self.logomark = Logomark(
            ilambda=self.ilambda,
            color_style=self.logomark_color_style,
            clear_space=self.clear_space,
        )

    def _init_cap_height(self):
        if self.logotype_cap_height is None:
            self.logotype_cap_height = (
                self.lambda_radius * (1 + self.lambda_thickness * 2) * math.sqrt(3)
            )

    def _init_logotype(self):
        self.loader = FontLoader(capHeight=self.logotype_cap_height)
        self.logotype = Logotype(
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
        logomark_box = self.logomark.elements_bounding_box
        logotype_box = self.logotype.elements_bounding_box
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

    def _get_clearspace(self):
        return self.logomark._get_clearspace()

    def make_svg_elements(self):
        return self.make_svg_background() + (
            self.logomark.make_svg_elements(),
            svg.G(
                transform=[self.logotype_transform],
                elements=self.logotype.make_svg_elements(),
            ),
        )

    def write_svg(self):
        with open(Path("test-logo.svg"), "w") as file:
            file.write(str(self.make_svg()))


if __name__ == "__main__":
    NixosLogo(background_color="#dddddd").write_svg()
