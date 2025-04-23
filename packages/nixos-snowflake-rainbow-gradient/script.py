from pathlib import Path

from nixoslogo.core import RAINBOW_COLORS, ColorStyle
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
snow_flake = Logomark(
    ilambda=ilambda,
    colors=RAINBOW_COLORS,
    color_style=ColorStyle.GRADIENT,
)

with open(Path("nixos-snowflake-rainbow-gradient.svg"), "w") as file:
    file.write(str(snow_flake.make_svg()))
