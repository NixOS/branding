from pathlib import Path

from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import (
    DimensionedLambda,
    DimensionedLogomarkGradientBackground,
)

# TODO @djacu see if this can be better
annotations = Annotations.small()
annotations.object_lines.stroke = "white"
annotations.construction_lines.stroke = "black"

ilambda = DimensionedLambda(
    annotations=annotations,
)

snow_flake = DimensionedLogomarkGradientBackground(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)

with open(Path("nixos-lambda-gradient-background.svg"), "w") as file:
    file.write(str(snow_flake.draw_lambda_with_gradients_background()))
