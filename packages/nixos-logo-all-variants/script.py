import itertools

from nixoslogo.core import (
    DEFAULT_LOGOTYPE_SPACINGS,
    DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
    ClearSpace,
    ColorStyle,
    LogoLayout,
    LogomarkColors,
    LogotypeStyle,
)
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Logomark
from nixoslogo.logotype import FontLoader, Logotype

background_color = "#dddddd"

# Logo horizontal layout
for (
    logomark_colors,
    logomark_color_style,
    logotype_color,
    logotype_style,
    clear_space,
) in itertools.product(
    LogomarkColors,
    ColorStyle,
    ("black", "white"),
    LogotypeStyle,
    ClearSpace,
):
    logo = NixosLogo(
        background_color=background_color,
        logo_layout=LogoLayout.HORIZONTAL,
        logotype_spacings=DEFAULT_LOGOTYPE_SPACINGS_WITH_BEARING,
        logomark_colors=logomark_colors,
        logomark_color_style=logomark_color_style,
        logotype_color=logotype_color,
        logotype_style=logotype_style,
        clear_space=clear_space,
    )
    logo.write_svg()
    logo.close()

# Logo vertical layout
for (
    logomark_colors,
    logomark_color_style,
    logotype_color,
    logotype_style,
    clear_space,
) in itertools.product(
    LogomarkColors,
    ColorStyle,
    ("black", "white"),
    LogotypeStyle,
    ClearSpace,
):
    logo = NixosLogo(
        background_color=background_color,
        logo_layout=LogoLayout.VERTICAL,
        logotype_spacings=DEFAULT_LOGOTYPE_SPACINGS,
        logomark_colors=logomark_colors,
        logomark_color_style=logomark_color_style,
        logotype_color=logotype_color,
        logotype_style=logotype_style,
        clear_space=clear_space,
    )
    logo.write_svg()
    logo.close()

# Logomark
for (
    logomark_colors,
    logomark_color_style,
    clear_space,
) in itertools.product(
    LogomarkColors,
    ColorStyle,
    ClearSpace,
):
    logo = Logomark(
        background_color=background_color,
        colors=logomark_colors,
        color_style=logomark_color_style,
        clear_space=clear_space,
    )
    logo.write_svg()

# Logotype
for (
    logotype_color,
    logotype_style,
    clear_space,
) in itertools.product(
    ("black", "white"),
    LogotypeStyle,
    ClearSpace,
):
    loader = FontLoader()
    logo = Logotype(
        loader=loader,
        background_color=background_color,
        logotype_spacings=DEFAULT_LOGOTYPE_SPACINGS,
        color=logotype_color,
        style=logotype_style,
        clear_space=clear_space,
    )
    logo.write_svg()
    loader.font.close()
