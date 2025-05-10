from nixoslogo.annotations import Annotations
from nixoslogo.dimensioned import DimensionedLambdaLinear

ilambda = DimensionedLambdaLinear(
    annotations=Annotations.small(),
)
ilambda.write_svg()
