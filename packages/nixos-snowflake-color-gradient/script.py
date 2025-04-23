from pathlib import Path

from nixoslogo.core import ColorStyle
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
snow_flake = Logomark(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
)

with open(Path("nixos-snowflake-color-gradient.svg"), "w") as file:
    file.write(str(snow_flake.make_svg()))
