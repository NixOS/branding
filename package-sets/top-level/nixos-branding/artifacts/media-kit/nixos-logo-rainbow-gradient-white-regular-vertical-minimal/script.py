from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS,
    ClearSpace,
    ColorStyle,
    LogoLayout,
    LogomarkColors,
    LogotypeStyle,
)
from nixoslogo.logo import NixosLogo

logo = NixosLogo(
    logomark_colors=LogomarkColors.RAINBOW,
    logomark_color_style=ColorStyle.GRADIENT,
    logotype_color="white",
    logotype_style=LogotypeStyle.REGULAR,
    logotype_spacings=DEFAULT_LOGOTYPE_SPACINGS,
    logotype_characters="NixOS",
    logo_layout=LogoLayout.VERTICAL,
    clear_space=ClearSpace.MINIMAL,
)
logo.write_svg()
