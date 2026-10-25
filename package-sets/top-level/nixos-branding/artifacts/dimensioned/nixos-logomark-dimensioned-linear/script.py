from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomark

annotations = Annotations.medium()

logomark = DimensionedLogomark(
    color_style=ColorStyle.FLAT,
    annotations=annotations,
)
logomark.write_svg()
