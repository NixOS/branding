from pathlib import Path

from nixoslogo.annotations import Annotations
from nixoslogo.dimensioned import DimensionedLambda

lambda_inst = DimensionedLambda(
    annotations=Annotations.small(),
)

with open(Path("nixos-lambda-dimensioned-linear.svg"), "w") as file:
    file.write(str(lambda_inst.draw_lambda_linear_dimensions()))
