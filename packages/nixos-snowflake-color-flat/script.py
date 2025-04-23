from pathlib import Path

from nixoslogo.core import ColorStyle
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
snow_flake = Logomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
)

with open(Path("nixos-snowflake-color-flat.svg"), "w") as file:
    file.write(str(snow_flake.make_svg()))
