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
    logomark_colors=LogomarkColors.WHITE,
    logomark_color_style=ColorStyle.FLAT,
    logotype_color="white",
    logotype_style=LogotypeStyle.REGULAR,
    logotype_spacings=DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    logotype_characters="NixOS",
    logo_layout=LogoLayout.VERTICAL,
    clear_space=ClearSpace.RECOMMENDED,
)
logo.write_svg()
