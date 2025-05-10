from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import (
    DimensionedLambda,
    DimensionedLogomarkGradientBackground,
)

# TODO @djacu see if this can be better
annotations = Annotations.small()
annotations.object_lines.stroke = "white"
annotations.construction_lines.stroke = "black"

ilambda = DimensionedLambda(
    annotations=annotations,
)

logomark = DimensionedLogomarkGradientBackground(
    ilambda=ilambda,
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
