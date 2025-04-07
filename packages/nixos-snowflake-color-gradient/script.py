from pathlib import Path

from nixoslogo.snowflake import SnowFlakeGradient

object_lines = None
construction_lines = None
dimension_lines = None
radius = 512
snow_flake = SnowFlakeGradient(
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
    min_x=-2.25 * radius,
    min_y=-2.25 * radius,
    width=4.5 * radius,
    height=4.5 * radius,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)

with open(Path("nixos-snowflake-color-gradient.svg"), "w") as file:
    file.write(str(snow_flake.draw_clean_flake_gradient()))
