from nixoslogo.core import ClearSpace, ColorStyle, LogomarkColors
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
logomark = Logomark(
    ilambda=ilambda,
    colors=LogomarkColors.TRANS,
    color_style=ColorStyle.GRADIENT,
    clear_space=ClearSpace.MINIMAL,
)
logomark.write_svg()
