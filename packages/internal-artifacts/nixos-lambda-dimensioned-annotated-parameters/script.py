from nixoslogo.annotations import Annotations
from nixoslogo.dimensioned import DimensionedLambdaAnnotatedParameters

ilambda = DimensionedLambdaAnnotatedParameters(
    annotations=Annotations.small(),
)
ilambda.write_svg()
