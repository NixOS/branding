from pathlib import Path

from nixoslogo.colors import ColorStyle
from nixoslogo.lines import ConstructionLines, DimensionLines, LineGroup
from nixoslogo.snowflake import DimensionedLambda, DimensionedSnowFlake
from nixoslogo.svghelpers import ImageParameters

object_lines = LineGroup(
    name="object",
    stroke="green",
    stroke_width=8,
    font_size="4rem",
)
construction_lines = ConstructionLines(
    name="construction",
    stroke="blue",
    stroke_width=4,
    font_size="4rem",
)
dimension_lines = DimensionLines(
    name="dimension",
    stroke="red",
    stroke_width=2,
    font_size="4rem",
)

radius = 512

image_parameters = ImageParameters(
    min_x=-4 * radius,
    min_y=-4 * radius,
    width=8 * radius,
    height=8 * radius,
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
    color_style=ColorStyle.FLAT,
    image_parameters=image_parameters,
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

with open(Path("nixos-snowflake-dimensioned-linear.svg"), "w") as file:
    file.write(str(snow_flake.draw_flake_linear_dimensions()))
