from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomarkGradientBackground

# TODO @djacu see if this can be better
annotations = Annotations.small()
annotations.object_lines.stroke = "white"
annotations.construction_lines.stroke = "black"

logomark = DimensionedLogomarkGradientBackground(
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
