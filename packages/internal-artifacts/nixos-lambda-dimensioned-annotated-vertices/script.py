from nixoslogo.annotations import Annotations
from nixoslogo.dimensioned import DimensionedLambdaAnnotatedVertices

ilambda = DimensionedLambdaAnnotatedVertices(
    annotations=Annotations.small(),
)
ilambda.write_svg()
