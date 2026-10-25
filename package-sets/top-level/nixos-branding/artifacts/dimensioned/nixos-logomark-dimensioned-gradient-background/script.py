from nixoslogo.annotations import Annotations
from nixoslogo.core import ColorStyle
from nixoslogo.dimensioned import DimensionedLogomarkGradientBackground

annotations = Annotations.small(
    overrides={
        "object_lines": {"stroke": "white"},
        "construction_lines": {"stroke": "black"},
    }
)

logomark = DimensionedLogomarkGradientBackground(
    color_style=ColorStyle.GRADIENT,
    annotations=annotations,
)
logomark.write_svg()
