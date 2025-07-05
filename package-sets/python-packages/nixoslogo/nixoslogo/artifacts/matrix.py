import logging
from pathlib import Path

import svg
from svgpathtools import svg2paths2

from nixoslogo.core import (
    NIXOS_DARK_BLUE,
    NIXOS_LIGHT_BLUE,
    BaseRenderable,
    ClearSpace,
    LogomarkColors,
)
from nixoslogo.logging_config import setup_logging
from nixoslogo.logomark import Logomark

logger = logging.getLogger(__name__)


class NixosMatrixLogo(BaseRenderable):
    def __init__(
        self,
        other: Path = Path("./python3.svg"),
        **kwargs,
    ):
        self.other = other
        self.other_clearspace = 0
        self.divider_height = 24
        self.width = 1024
        self.height = 1024
        self.logomark = Logomark(
            colors=LogomarkColors.WHITE,
            clear_space=ClearSpace.MINIMAL,
        )
        super().__init__(
            **kwargs,
        )

    def _get_clearspace(self):
        return 0

    def make_filename(self, extras: tuple[str] = ()):
        return "-".join(
            [
                "nixos",
                "matrix",
                "logo",
            ]
            + list(extras)
        )

    @property
    def elements_bounding_box(self) -> tuple[float, float, float, float]:
        return (
            -self.width / 2,
            -self.height / 2,
            self.width / 2,
            self.height / 2,
        )

    def _make_other_element(self):
        other_list, other_paths, other_attrs = svg2paths2(self.other)

        print(other_list)
        print(other_attrs)
        print(other_paths)

        renamed_paths = (
            {key.replace("-", "_"): value for key, value in path.items()}
            for path in other_paths
        )
        clean_paths = (
            {
                key: value
                for key, value in path.items()
                if key in ["d", "fill", "fill_rule", "clip_rule"]
            }
            for path in renamed_paths
        )
        paths = tuple(svg.Path(**paths) for paths in clean_paths)

        # print(paths)

        match other_attrs:
            case {"width": width, "height": height, "viewBox": viewbox}:
                minx, miny, width, height = map(viewbox, float)
            case {"width": width, "height": height}:
                minx = 0
                miny = 0
                width = float(width)
                height = float(height)
            case {"viewBox": viewbox}:
                minx, miny, width, height = map(viewbox, float)
            case _:
                print("No match or unexpected keys")

        return svg.G(
            transform=[
                svg.Translate(0, -(self.height + self.divider_height) / 4),
                svg.Scale(
                    (self.canvas.height - self.divider_height)
                    / (height - miny)
                    / 2
                    / (1 + 2 * self.other_clearspace)
                ),
                svg.Translate(
                    -(width - minx) / 2,
                    -(height - miny) / 2,
                ),
            ],
            elements=paths,
        )

    def make_svg_elements(self):
        return (
            svg.Rect(
                x=-self.width / 2,
                y=-self.divider_height / 2,
                width=self.width,
                height=self.divider_height,
                fill="white",
            ),
            svg.Rect(
                x=-self.width / 2,
                y=-self.height / 2,
                width=self.width,
                height=self.height / 2 - self.divider_height / 2,
                fill=NIXOS_LIGHT_BLUE.convert("srgb").to_string(hex=True),
            ),
            svg.Rect(
                x=-self.width / 2,
                y=+self.divider_height / 2,
                width=self.width,
                height=self.height / 2 - self.divider_height / 2,
                fill=NIXOS_DARK_BLUE.convert("srgb").to_string(hex=True),
            ),
            svg.G(
                transform=[
                    svg.Translate(0, self.height / 4),
                    svg.Scale(
                        (self.canvas.height - self.divider_height)
                        / self.logomark.canvas.height
                        / 2
                    ),
                ],
                elements=self.logomark.make_svg_elements(),
            ),
            self._make_other_element(),
        )


if __name__ == "__main__":
    setup_logging(level=logging.DEBUG)

    logo = NixosMatrixLogo(background_color="#dddddd")
    logo.write_svg(filename=logo.make_filename(extras=("test",)))
