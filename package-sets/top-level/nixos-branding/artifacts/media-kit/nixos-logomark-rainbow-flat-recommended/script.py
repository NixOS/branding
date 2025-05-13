from nixoslogo.core import ClearSpace, ColorStyle, LogomarkColors
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
logomark = Logomark(
    ilambda=ilambda,
    colors=LogomarkColors.RAINBOW,
    color_style=ColorStyle.FLAT,
    clear_space=ClearSpace.RECOMMENDED,
)
logomark.write_svg()
