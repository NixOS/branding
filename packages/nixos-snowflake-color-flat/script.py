from pathlib import Path

from nixoslogo.core import ColorStyle
from nixoslogo.layout import Canvas
from nixoslogo.logomark import Lambda, Logomark

radius = 512

canvas = Canvas(
    min_x=-2.25 * radius,
    min_y=-2.25 * radius,
    width=4.5 * radius,
    height=4.5 * radius,
)

ilambda = Lambda(
    canvas=canvas,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)
snow_flake = Logomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
    canvas=canvas,
)

with open(Path("nixos-snowflake-color-flat.svg"), "w") as file:
    file.write(str(snow_flake.draw_snowflake()))
