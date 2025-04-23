from pathlib import Path

from nixoslogo.annotations import ConstructionLines, DimensionLines, LineGroup
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLambda, DimensionedLogomark
from nixoslogo.layout import Canvas

object_lines = LineGroup(
    name="object",
    stroke="white",
    stroke_width=4,
    font_size="2rem",
    fill="transparent",
)
construction_lines = ConstructionLines(
    name="construction",
    stroke="black",
    stroke_width=2,
    font_size="2rem",
)
dimension_lines = DimensionLines(
    name="dimension",
    stroke="red",
    stroke_width=1,
    font_size="2rem",
)

radius = 512

canvas = Canvas(
    min_x=-2 * radius,
    min_y=-2 * radius,
    width=4 * radius,
    height=4 * radius,
)

ilambda = DimensionedLambda(
    canvas=canvas,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

snow_flake = DimensionedLogomark(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    canvas=canvas,
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

with open(Path("nixos-lambda-gradient-background.svg"), "w") as file:
    file.write(str(snow_flake.draw_lambda_with_gradients_background()))
