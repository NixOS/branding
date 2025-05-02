from pathlib import Path

from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import (
    DimensionedLambda,
    DimensionedLogomarkGradientAnnotated,
)

annotations = Annotations.small()

ilambda = DimensionedLambda(
    annotations=annotations,
)

snow_flake = DimensionedLogomarkGradientAnnotated(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)

with open(Path("nixos-lambda-gradient-dimensioned.svg"), "w") as file:
    file.write(str(snow_flake.draw_lambda_with_gradients_line()))
