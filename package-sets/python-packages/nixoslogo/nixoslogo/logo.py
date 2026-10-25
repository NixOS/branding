import math
from typing import override

import svg

from nixoslogo.colors import Color
from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    BaseRenderable,
    ClearSpace,
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


class NixosLogo(BaseRenderable):
    def __init__(
        self,
        lambda_radius: int = 512,
        lambda_thickness: float = 1 / 4,
        lambda_gap: float = 1 / 32,
        loader: FontLoader | None = None,
        logo_layout: LogoLayout = LogoLayout.HORIZONTAL,
        logomark_colors: LogomarkColors | tuple[Color, ...] = LogomarkColors.DEFAULT,
        logomark_color_style: ColorStyle = ColorStyle.GRADIENT,
        logotype_cap_height: float | None = None,
        logotype_color: str = "black",
        logotype_style: LogotypeStyle = LogotypeStyle.REGULAR,
        logotype_spacings: tuple[int, ...] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
        logotype_characters: str = "NixOS",
        logotype_transform: svg.Translate | None = None,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        **kwargs,
    ):
        self.lambda_radius: int = lambda_radius
        self.lambda_thickness: float = lambda_thickness
        self.lambda_gap: float = lambda_gap
        self.logo_layout: LogoLayout = logo_layout
        self.logomark_colors: LogomarkColors | tuple[Color, ...] = logomark_colors
        self.logomark_color_style: ColorStyle = logomark_color_style
        self.logotype_color: str = logotype_color
        self.logotype_style: LogotypeStyle = logotype_style
        self.logotype_spacings: tuple[int, ...] = logotype_spacings
        self.logotype_characters: str = logotype_characters
        self.clear_space: ClearSpace = clear_space

        self._init_snowflake()
        self.logotype_cap_height: float = (
            logotype_cap_height
            if logotype_cap_height is not None
            else self._default_cap_height()
        )
        self.loader: FontLoader = (
            loader
            if loader is not None
            else FontLoader(capHeight=self.logotype_cap_height)
        )
        self._init_logotype()
        self.logotype_transform: svg.Translate = (
            logotype_transform
            if logotype_transform is not None
            else self._default_transform()
        )

        super().__init__(clear_space=clear_space, **kwargs)

    def _init_snowflake(self):
        self.ilambda: Lambda = Lambda(
            radius=self.lambda_radius,
            thickness=self.lambda_thickness,
            gap=self.lambda_gap,
        )
        self.logomark: Logomark = Logomark(
            ilambda=self.ilambda,
            colors=self.logomark_colors,
            color_style=self.logomark_color_style,
            clear_space=self.clear_space,
        )

    def _default_cap_height(self) -> float:
        return self.lambda_radius * (1 + self.lambda_thickness * 2) * math.sqrt(3)

    def _init_logotype(self):
        self.logotype: Logotype = Logotype(
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
                    self.logotype_cap_height / 2,
                )
            case LogoLayout.VERTICAL:
                return svg.Translate(
                    -self.logotype.elements_width / 2,
                    self.logomark.inradius + self.logotype_cap_height * 1.25,
                )

    @property
    @override
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        logomark_box = self.logomark.elements_bounding_box
        logotype_box = self.logotype.elements_bounding_box
        offset_x = float(self.logotype_transform.x)
        offset_y = float(self.logotype_transform.y or 0)
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
                transform=[self.logotype_transform],
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
