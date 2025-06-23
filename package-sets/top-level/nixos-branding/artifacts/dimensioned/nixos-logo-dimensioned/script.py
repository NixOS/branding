from nixoslogo.annotations import Annotations
from nixoslogo.core import ClearSpace
from nixoslogo.dimensioned import DimensionedLogo

# TODO @djacu see if this can be better
annotations = Annotations.large()
annotations.construction_lines.stroke = "black"

logo = DimensionedLogo(
    clear_space=ClearSpace.MINIMAL,
    annotations=annotations,
)
logo.write_svg()
