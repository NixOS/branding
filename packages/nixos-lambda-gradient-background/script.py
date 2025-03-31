from pathlib import Path

from nixoslogo.lines import LineGroup
from nixoslogo.snowflake import SnowFlakeGradient

object_lines = LineGroup(
    name="object",
    stroke="white",
    stroke_width=4,
    font_size="2rem",
    fill="transparent",
)
construction_lines = LineGroup(
    name="construction",
    stroke="black",
    stroke_width=2,
    font_size="2rem",
)
dimension_lines = LineGroup(
    name="dimension",
    stroke="red",
    stroke_width=1,
    font_size="2rem",
)
radius = 512
snow_flake = SnowFlakeGradient(
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
    min_x=-2 * radius,
    min_y=-2 * radius,
    width=4 * radius,
    height=4 * radius,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)

with open(Path("nixos-lambda-gradient-background.svg"), "w") as file:
    file.write(str(snow_flake.draw_lambda_with_gradients_background()))
