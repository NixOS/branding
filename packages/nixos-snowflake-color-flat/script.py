from pathlib import Path

from nixoslogo.colors import ColorStyle
from nixoslogo.logomark import Lambda, Logomark
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
snow_flake = Logomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
    image_parameters=image_parameters,
)

with open(Path("nixos-snowflake-color-flat.svg"), "w") as file:
    file.write(str(snow_flake.draw_snowflake()))
