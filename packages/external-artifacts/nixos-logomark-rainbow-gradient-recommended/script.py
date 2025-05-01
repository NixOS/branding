from nixoslogo.core import ColorStyle, LogomarkColors
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
logomark = Logomark(
    ilambda=ilambda,
    colors=LogomarkColors.RAINBOW,
    color_style=ColorStyle.GRADIENT,
)
logomark.write_svg()
