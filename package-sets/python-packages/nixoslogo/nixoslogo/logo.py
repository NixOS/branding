import math

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
        logomark_colors: LogomarkColors | tuple[Color] = LogomarkColors.DEFAULT,
        logomark_color_style: ColorStyle = ColorStyle.GRADIENT,
        logotype_cap_height: float | None = None,
        logotype_color: str = "black",
        logotype_style: LogotypeStyle = LogotypeStyle.REGULAR,
        logotype_spacings: tuple[int] = DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
        logotype_characters: str = "NixOS",
        logotype_transform: svg.Translate | None = None,
        clear_space: ClearSpace = ClearSpace.RECOMMENDED,
        **kwargs,
    ):
        self.lambda_radius = lambda_radius
        self.lambda_thickness = lambda_thickness
        self.lambda_gap = lambda_gap
        self.loader = loader
        self.logo_layout = logo_layout
        self.logomark_colors = logomark_colors
        self.logomark_color_style = logomark_color_style
        self.logotype_cap_height = logotype_cap_height
        self.logotype_color = logotype_color
        self.logotype_style = logotype_style
        self.logotype_spacings = logotype_spacings
        self.logotype_characters = logotype_characters
        self.logotype_transform = logotype_transform
        self.clear_space = clear_space

        self._init_snowflake()
        self._init_cap_height()
        self._init_logotype()
        self._init_layout()

        super().__init__(**kwargs)

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

    def _init_cap_height(self):
        if self.logotype_cap_height is None:
            self.logotype_cap_height = (
                self.lambda_radius * (1 + self.lambda_thickness * 2) * math.sqrt(3)
            )

    def _init_logotype(self):
        if self.loader is None:
            self.loader = FontLoader(capHeight=self.logotype_cap_height)
        self.logotype = Logotype(
            characters=self.logotype_characters,
            loader=self.loader,
            color=self.logotype_color,
            style=self.logotype_style,
            spacings=self.logotype_spacings,
        )

    def _init_layout(self):
        if self.logotype_transform is None:
            match self.logo_layout:
                case LogoLayout.HORIZONTAL:
                    self.logotype_transform = svg.Translate(
                        self.logomark.circumradius,
                        self.logotype_cap_height / 2,
                    )
                case LogoLayout.VERTICAL:
                    self.logotype_transform = svg.Translate(
                        -self.logotype.elements_width / 2,
                        self.logomark.inradius + self.logotype_cap_height * 1.25,
                    )
                case _:
                    raise Exception(f"Unknown LogoLayout: {self.logo_layout}")

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
        match self.clear_space:
            case ClearSpace.NONE:
                return 0
            case ClearSpace.MINIMAL:
                return self.logomark.elements_height / 2
            case ClearSpace.RECOMMENDED:
                return self.logomark.elements_height
            case _:
                raise Exception(f"Unknown ClearSpace: {self.clear_space}")

    def make_svg_elements(self):
        return (
            self.logomark.make_svg_elements(),
            svg.G(
                transform=[self.logotype_transform],
                elements=self.logotype.make_svg_elements(),
            ),
        )

    def make_filename(self, colors="default", extras: tuple[str] = ()):
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
