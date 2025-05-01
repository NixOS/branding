from nixoslogo.core import ColorStyle
from nixoslogo.logomark import Lambda, Logomark

ilambda = Lambda()
logomark = Logomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
)
logomark.write_svg()
