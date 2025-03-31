from typing import Self

from coloraide import Color as ColorBase

from .helpers import stable_hash


class Color(ColorBase):
    GRADIENT_LIGHTNESS_DELTA = -0.04
    GRADIENT_CHROMA_DELTA = -0.01

    def darken(self, scale) -> Self:
        """Clones and darkens the color. Only used for Lch-like colorspaces."""
        return (
            self.clone()
            .set(
                "lightness",
                lambda lightness: lightness + scale * self.GRADIENT_LIGHTNESS_DELTA,
            )
            .set("chroma", lambda chroma: chroma + scale * self.GRADIENT_CHROMA_DELTA)
        )

    def gradient_color_name(self) -> str:
        return f"linear-gradient-{stable_hash(self.to_string())}"


NIXOS_DARK_BLUE = Color("oklch", (0.5774, 0.1248, 264))
NIXOS_LIGHT_BLUE = Color("oklch", (0.7636, 0.0866, 240))
