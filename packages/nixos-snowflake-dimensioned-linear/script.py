from pathlib import Path

from nixoslogo.annotations import ConstructionLines, DimensionLines, LineGroup
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLambda, DimensionedLogomark

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

ilambda = DimensionedLambda(
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

snow_flake = DimensionedLogomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

with open(Path("nixos-snowflake-dimensioned-linear.svg"), "w") as file:
    file.write(str(snow_flake.draw_flake_linear_dimensions()))
