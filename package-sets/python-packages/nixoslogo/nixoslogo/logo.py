import math
from dataclasses import dataclass, field
from typing import override

import svg

from nixoslogo.colors import Color
from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    BaseRenderable,
    ColorStyle,
    LogoLayout,
    LogomarkColors,
    LogotypeStyle,
    flatten_svg_elements,
)
from nixoslogo.logomark import Lambda, Logomark
from nixoslogo.logotype import (
    FontLoader,
    Logotype,
)


@dataclass(kw_only=True)
class NixosLogo(BaseRenderable):
    lambda_radius: int = 512
    lambda_thickness: float = 1 / 4
    lambda_gap: float = 1 / 32
    logo_layout: LogoLayout = LogoLayout.HORIZONTAL
    logomark_colors: LogomarkColors | tuple[Color, ...] = LogomarkColors.DEFAULT
    logomark_color_style: ColorStyle = ColorStyle.GRADIENT
    logotype_cap_height: float | None = None
    logotype_color: str = "black"
    logotype_style: LogotypeStyle = LogotypeStyle.REGULAR
    logotype_spacings: tuple[int, ...] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING
    logotype_characters: str = "NixOS"
    logotype_transform: svg.Translate | None = None
    ilambda: Lambda = field(init=False)
    logomark: Logomark = field(init=False)
    loader: FontLoader = field(init=False)
    logotype: Logotype = field(init=False)

    def __post_init__(self) -> None:
        self._init_snowflake()
        cap_height = (
            self.logotype_cap_height
            if self.logotype_cap_height is not None
            else self._default_cap_height()
        )
        self.loader = FontLoader(capHeight=cap_height)
        self._init_logotype()

    @property
    def transform(self) -> svg.Translate:
        return (
            self.logotype_transform
            if self.logotype_transform is not None
            else self._default_transform()
        )

    def _init_snowflake(self):
        self.ilambda = Lambda(
            radius=self.lambda_radius,
            thickness=self.lambda_thickness,
            gap=self.lambda_gap,
        )
        self.logomark = Logomark(
            ilambda=self.ilambda,
            colors=self.logomark_colors,
            color_style=self.logomark_color_style,
            clear_space=self.clear_space,
        )

    def _default_cap_height(self) -> float:
        return self.lambda_radius * (1 + self.lambda_thickness * 2) * math.sqrt(3)

    def _init_logotype(self):
        self.logotype = Logotype(
            characters=self.logotype_characters,
            loader=self.loader,
            color=self.logotype_color,
            style=self.logotype_style,
            spacings=self.logotype_spacings,
        )

    def _default_transform(self) -> svg.Translate:
        match self.logo_layout:
            case LogoLayout.HORIZONTAL:
                return svg.Translate(
                    self.logomark.circumradius,
                    self.logotype.cap_height / 2,
                )
            case LogoLayout.VERTICAL:
                return svg.Translate(
                    -self.logotype.elements_width / 2,
                    self.logomark.inradius + self.logotype.cap_height * 1.25,
                )

    @property
    @override
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        logomark_box = self.logomark.elements_bounding_box
        logotype_box = self.logotype.elements_bounding_box
        offset_x = float(self.transform.x)
        offset_y = float(self.transform.y or 0)
        logotype_box_translated = (
            logotype_box[0] + offset_x,
            logotype_box[1] + offset_y,
            logotype_box[2] + offset_x,
            logotype_box[3] + offset_y,
        )
        min_x, min_y, max_x, max_y = (
            predicate(elem)
            for predicate, elem in zip(
                (min, min, max, max),
                list(zip(*(logomark_box, logotype_box_translated))),
            )
        )
        return (min_x, min_y, max_x, max_y)

    @property
    @override
    def clearspace_unit(self) -> float:
        return self.logomark.elements_height

    @override
    def make_svg_elements(self) -> list[svg.Element]:
        return flatten_svg_elements(
            self.logomark.make_svg_elements(),
            svg.G(
                transform=[self.transform],
                elements=self.logotype.make_svg_elements(),
            ),
        )

    @override
    def make_filename(self, extras: tuple[str, ...] = ()) -> str:
        return "-".join(
            [
                self.logotype_characters.lower(),
                "logo",
                self.logomark.colors_name.lower(),
                self.logomark_color_style.name.lower(),
                self.logotype_color,
                self.logotype_style.name.lower(),
                self.logo_layout.name.lower(),
                self.clear_space.name.lower(),
            ]
            + list(extras)
        )

    def close(self):
        self.loader.cleanup()


if __name__ == "__main__":
    logo = NixosLogo(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))
