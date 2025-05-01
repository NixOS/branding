from pathlib import Path

from nixoslogo.annotations import Annotations
from nixoslogo.core import (
    ColorStyle,
)
from nixoslogo.dimensioned import DimensionedLambda, DimensionedLogomark
from nixoslogo.layout import Canvas

radius = 512

canvas = Canvas(
    min_x=-2 * radius,
    min_y=-2 * radius,
    width=4 * radius,
    height=4 * radius,
)

annotations = Annotations.small()

ilambda = DimensionedLambda(
    radius=radius,
    annotations=annotations,
)

snow_flake = DimensionedLogomark(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    canvas=canvas,
    annotations=annotations,
)

with open(Path("nixos-lambda-gradient-dimensioned.svg"), "w") as file:
    file.write(str(snow_flake.draw_lambda_with_gradients_line()))
