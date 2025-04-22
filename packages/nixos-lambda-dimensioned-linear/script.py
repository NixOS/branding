from pathlib import Path

from nixoslogo.annotations import ConstructionLines, DimensionLines, LineGroup
from nixoslogo.dimensioned import DimensionedLambda
from nixoslogo.layout import Canvas

object_lines = LineGroup(
    name="object",
    stroke="green",
    stroke_width=4,
    font_size="2rem",
)
construction_lines = ConstructionLines(
    name="construction",
    stroke="blue",
    stroke_width=2,
    font_size="2rem",
)
dimension_lines = DimensionLines(
    name="dimension",
    stroke="red",
    stroke_width=1,
    font_size="2rem",
)

radius = 512

canvas = Canvas(
    min_x=-2 * radius,
    min_y=-2 * radius,
    width=4 * radius,
    height=4 * radius,
)

lambda_inst = DimensionedLambda(
    object_lines=object_lines,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
    canvas=canvas,
    radius=radius,
    thickness=1 / 4,
    gap=1 / 32,
)

with open(Path("nixos-lambda-dimensioned-linear.svg"), "w") as file:
    file.write(str(lambda_inst.draw_lambda_linear_dimensions()))
