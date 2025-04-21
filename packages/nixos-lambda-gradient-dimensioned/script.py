from pathlib import Path

from nixoslogo.colors import ColorStyle
from nixoslogo.lines import ConstructionLines, DimensionLines, LineGroup
from nixoslogo.logomark import DimensionedLambda, DimensionedSnowFlake
from nixoslogo.svghelpers import ImageParameters

object_lines = LineGroup(
    name="object",
    stroke="green",
    stroke_width=4,
    font_size="2rem",
)
construction_lines = ConstructionLines(
    name="construction",
    stroke="blue",
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

image_parameters = ImageParameters(
    min_x=-2 * radius,
    min_y=-2 * radius,
    width=4 * radius,
    height=4 * radius,
)

ilambda = DimensionedLambda(
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
    image_parameters=image_parameters,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)

snow_flake = DimensionedSnowFlake(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    image_parameters=image_parameters,
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

with open(Path("nixos-lambda-gradient-dimensioned.svg"), "w") as file:
    file.write(str(snow_flake.draw_lambda_with_gradients_line()))
