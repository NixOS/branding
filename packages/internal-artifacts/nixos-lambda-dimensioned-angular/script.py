from nixoslogo.annotations import Annotations
from nixoslogo.dimensioned import DimensionedLambdaAngular

ilambda = DimensionedLambdaAngular(
    annotations=Annotations.small(),
)
ilambda.write_svg()
