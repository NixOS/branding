from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    ClearSpace,
    ColorStyle,
    LogoLayout,
    LogomarkColors,
    LogotypeStyle,
)
from nixoslogo.logo import NixosLogo

logo = NixosLogo(
    clear_space=ClearSpace.RECOMMENDED,
    logo_layout=LogoLayout.HORIZONTAL,
    logomark_color_style=ColorStyle.GRADIENT,
    logomark_colors=LogomarkColors.DEFAULT,
    logotype_characters="NixOS",
    logotype_color="black",
    logotype_spacings=DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    logotype_style=LogotypeStyle.REGULAR,
)
logo.write_svg()
