from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLambda, DimensionedLogomark

annotations = Annotations.medium()

ilambda = DimensionedLambda(
    annotations=annotations,
)

logomark = DimensionedLogomark(
    ilambda=ilambda,
    color_style=ColorStyle.FLAT,
    annotations=annotations,
)
logomark.write_svg()
