from nixoslogo.annotations import Annotations
from nixoslogo.core import ClearSpace
from nixoslogo.dimensioned import DimensionedLogo

annotations = Annotations.large(overrides={"construction_lines": {"stroke": "black"}})

logo = DimensionedLogo(
    clear_space=ClearSpace.MINIMAL,
    annotations=annotations,
)
logo.write_svg()
