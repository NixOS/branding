from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import (
    DimensionedLambda,
    DimensionedLogomarkGradientAnnotated,
)

annotations = Annotations.small()

ilambda = DimensionedLambda(
    annotations=annotations,
)

logomark = DimensionedLogomarkGradientAnnotated(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
