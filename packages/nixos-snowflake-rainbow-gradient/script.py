from pathlib import Path

from nixoslogo.colors import Color, ColorStyle
from nixoslogo.logomark import Lambda, SnowFlake
from nixoslogo.svghelpers import ImageParameters

radius = 512

image_parameters = ImageParameters(
    min_x=-2.25 * radius,
    min_y=-2.25 * radius,
    width=4.5 * radius,
    height=4.5 * radius,
)

ilambda = Lambda(
    image_parameters=image_parameters,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)

snow_flake = SnowFlake(
    ilambda=ilambda,
    colors=(
        Color("oklch", (0.51, 0.208963, 29.2339)),
        Color("oklch", (0.70, 0.204259, 43.491)),
        Color("oklch", (0.81, 0.168100, 76.78)),
        Color("oklch", (0.60, 0.175100, 147.56)),
        Color("oklch", (0.60, 0.141400, 241.38)),
        Color("oklch", (0.46, 0.194300, 288.71)),
    ),
    color_style=ColorStyle.GRADIENT,
    image_parameters=image_parameters,
)

with open(Path("nixos-snowflake-rainbow-gradient.svg"), "w") as file:
    file.write(str(snow_flake.draw_snowflake()))
