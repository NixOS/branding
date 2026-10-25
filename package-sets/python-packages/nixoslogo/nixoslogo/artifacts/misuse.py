import logging
from dataclasses import dataclass
from typing import override

import svg

from nixoslogo.core import ClearSpace, flatten_svg_elements
from nixoslogo.layout import Canvas
from nixoslogo.logging_config import setup_logging
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Logomark

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class LogomarkRotate(Logomark):
    clear_space: ClearSpace = ClearSpace.MINIMAL

    @override
    def make_filename(self, extras: tuple[str, ...] = ()):
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
    @override
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        return (
            -self.inradius,
            -self.circumradius,
            self.inradius,
            self.circumradius,
        )

    @override
    def make_svg_elements(self) -> list[svg.Element]:
        return flatten_svg_elements(
            svg.G(
                transform=[svg.Rotate(30)],
                elements=super().make_svg_elements(),
            ),
        )


@dataclass(kw_only=True)
class LogomarkMirror(Logomark):
    clear_space: ClearSpace = ClearSpace.MINIMAL

    @override
    def make_filename(self, extras: tuple[str, ...] = ()):
        return "-".join(
            [
                "nixos",
                "logomark",
                "misuse",
                "mirror",
            ]
            + list(extras)
        )

    @override
    def make_svg_elements(self) -> list[svg.Element]:
        return flatten_svg_elements(
            svg.G(
                transform=[svg.Scale(-1, 1)],
                elements=super().make_svg_elements(),
            ),
        )


@dataclass(kw_only=True)
class LogoCrop(NixosLogo):
    clear_space: ClearSpace = ClearSpace.MINIMAL

    @override
    def make_filename(self, extras: tuple[str, ...] = ()):
        return "-".join(
            [
                "nixos",
                "logo",
                "misuse",
                "crop",
            ]
            + list(extras)
        )

    @override
    def make_canvas(self, clear_space: ClearSpace) -> Canvas:
        min_x, min_y, max_x, max_y = self.elements_bounding_box
        distance = clear_space.distance(self.clearspace_unit)

        min_x += distance
        min_y -= distance
        max_x -= distance
        max_y += distance

        return Canvas(
            min_x=min_x,
            min_y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )


if __name__ == "__main__":
    setup_logging(level=logging.DEBUG)

    logo = LogomarkRotate(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))

    logo = LogomarkMirror(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))

    logo = LogoCrop(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))
