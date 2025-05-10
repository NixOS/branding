from nixoslogo.core import ColorStyle
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
logomark = Logomark(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
)
logomark.write_svg()
