from pathlib import Path

from nixoslogo.lines import LineGroup
from nixoslogo.snowflake import Lambda, SnowFlake

object_lines = LineGroup(
    name="object",
    stroke="green",
    stroke_width=8,
    font_size="4rem",
)
construction_lines = LineGroup(
    name="construction",
    stroke="blue",
    stroke_width=4,
    font_size="4rem",
)
dimension_lines = LineGroup(
    name="dimension",
    stroke="red",
    stroke_width=2,
    font_size="4rem",
)
radius = 512
ilambda = Lambda(
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
    min_x=-4 * radius,
    min_y=-4 * radius,
    width=8 * radius,
    height=8 * radius,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)
snow_flake = SnowFlake(
    ilambda=ilambda,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
    min_x=-4 * radius,
    min_y=-4 * radius,
    width=8 * radius,
    height=8 * radius,
)

with open(Path("nixos-snowflake-dimensioned-linear.svg"), "w") as file:
    file.write(str(snow_flake.draw_flake_linear_dimensions()))
