from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomarkGradientAnnotated

annotations = Annotations.small()

logomark = DimensionedLogomarkGradientAnnotated(
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
