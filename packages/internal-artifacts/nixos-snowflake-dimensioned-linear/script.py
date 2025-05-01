from pathlib import Path

from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLambda, DimensionedLogomark

annotations = Annotations.medium()

ilambda = DimensionedLambda(
    annotations=annotations,
)

snow_flake = DimensionedLogomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
    annotations=annotations,
)

with open(Path("nixos-snowflake-dimensioned-linear.svg"), "w") as file:
    file.write(str(snow_flake.draw_flake_linear_dimensions()))
