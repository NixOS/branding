from nixoslogo.core import ClearSpace, ColorStyle, LogomarkColors
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
logomark = Logomark(
    ilambda=ilambda,
    colors=LogomarkColors.RAINBOW,
    color_style=ColorStyle.GRADIENT,
    clear_space=ClearSpace.NONE,
)
logomark.write_svg()
