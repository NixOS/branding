import logging

import svg

from nixoslogo.core import ClearSpace, LogotypeStyle
from nixoslogo.layout import Canvas
from nixoslogo.logging_config import setup_logging
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Logomark

logger = logging.getLogger(__name__)


class LogomarkRotate(Logomark):
    def __init__(
        self,
        clear_space: ClearSpace = ClearSpace.MINIMAL,
        **kwargs,
    ):
        self.clear_space = clear_space
        super().__init__(
            clear_space=clear_space,
            **kwargs,
        )

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "logomark",
                "misuse",
                "rotate",
            ]
            + list(extras)
        )

    @property
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        return (
            -self.inradius,
            -self.circumradius,
            self.inradius,
            self.circumradius,
        )

    def make_svg_elements(self):
        return (
            svg.G(
                transform=[svg.Rotate(30)],
                elements=super().make_svg_elements(),
            ),
        )


class LogomarkMirror(Logomark):
    def __init__(
        self,
        clear_space: ClearSpace = ClearSpace.MINIMAL,
        **kwargs,
    ):
        self.clear_space = clear_space
        super().__init__(
            clear_space=clear_space,
            **kwargs,
        )

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "logomark",
                "misuse",
                "mirror",
            ]
            + list(extras)
        )

    def make_svg_elements(self):
        return (
            svg.G(
                transform=[svg.Scale(-1, 1)],
                elements=super().make_svg_elements(),
            ),
        )


class LogoCrop(NixosLogo):
    def __init__(
        self,
        clear_space: ClearSpace = ClearSpace.MINIMAL,
        **kwargs,
    ):
        self.clear_space = clear_space
        super().__init__(
            clear_space=clear_space,
            **kwargs,
        )

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "logo",
                "misuse",
                "crop",
            ]
            + list(extras)
        )

    def _init_canvas(self):
        if self.canvas is None:
            min_x, min_y, max_x, max_y = self.elements_bounding_box
            clear_space = self._get_clearspace()

            min_x += clear_space
            min_y -= clear_space
            max_x -= clear_space
            max_y += clear_space

            self.canvas = Canvas(
                min_x=min_x,
                min_y=min_y,
                width=max_x - min_x,
                height=max_y - min_y,
            )


class LogoScale(NixosLogo):
    def __init__(
        self,
        clear_space: ClearSpace = ClearSpace.MINIMAL,
        **kwargs,
    ):
        self.clear_space = clear_space
        super().__init__(
            clear_space=clear_space,
            **kwargs,
        )

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "logo",
                "misuse",
                "scale",
            ]
            + list(extras)
        )

    def _init_cap_height(self):
        if self.logotype_cap_height is None:
            self.logotype_cap_height = self.lambda_radius


class LogoColorsWithLambdaPrime(NixosLogo):
    def __init__(
        self,
        clear_space: ClearSpace = ClearSpace.MINIMAL,
        logotype_style: LogotypeStyle = LogotypeStyle.LAMBDAPRIME,
        **kwargs,
    ):
        self.clear_space = clear_space
        super().__init__(
            clear_space=clear_space,
            logotype_style=logotype_style,
            **kwargs,
        )

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "logo",
                "misuse",
                "lambdaprime",
            ]
            + list(extras)
        )


if __name__ == "__main__":
    setup_logging(level=logging.DEBUG)

    logo = LogomarkRotate(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))

    logo = LogomarkMirror(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))

    logo = LogoCrop(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))

    logo = LogoScale(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))

    logo = LogoColorsWithLambdaPrime(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))
