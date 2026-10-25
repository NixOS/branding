from nixoslogo.annotations import Annotations
from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS, ClearSpace
from nixoslogo.dimensioned import DimensionedLogotype
from nixoslogo.logotype import FontLoader

annotations = Annotations.small(
    overrides={"construction_lines": {"stroke": "black", "stroke_dasharray": [16]}}
)

loader = FontLoader(capHeight=512)

logotype = DimensionedLogotype(
    loader=loader,
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
    clear_space=ClearSpace.MINIMAL,
    annotations=annotations,
)
logotype.write_svg()
