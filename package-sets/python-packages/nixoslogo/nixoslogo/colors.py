from typing import Self

from coloraide import Color as ColorBase

from .helpers import stable_hash


class Color(ColorBase):
    GRADIENT_LIGHTNESS_DELTA = -0.04
    GRADIENT_CHROMA_DELTA = -0.01

    def darken(self, scale: float) -> Self:
        """Clones and darkens the color. Only used for Lch-like colorspaces."""

        def darker_lightness(lightness: float) -> float:
            return max(0, lightness + scale * self.GRADIENT_LIGHTNESS_DELTA)

        def darker_chroma(chroma: float) -> float:
            return max(0, chroma + scale * self.GRADIENT_CHROMA_DELTA)

        return (
            self.clone().set("lightness", darker_lightness).set("chroma", darker_chroma)
        )

    def gradient_color_name(self) -> str:
        return f"linear-gradient-{stable_hash(self.to_string())}"
