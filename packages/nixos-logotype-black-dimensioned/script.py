from pathlib import Path

from nixoslogo.annotations import ConstructionLines, DimensionLines
from nixoslogo.dimensioned import DimensionedLogotype
from nixoslogo.logotype import (
    DEFAULT_LOGOTYPE_SPACINGS,
    Character,
    FontLoader,
)

construction_lines = ConstructionLines(
    name="construction",
    stroke="black",
    stroke_width=2,
    stroke_dasharray=16,
    font_size="2rem",
)
dimension_lines = DimensionLines(
    name="dimension",
    stroke="red",
    stroke_width=1,
    font_size="2rem",
)

loader = FontLoader(capHeight=512)

my_char_dim = DimensionedLogotype(
    characters=[
        Character(character="N", loader=loader),
        Character(character="i", loader=loader),
        Character(character="x", loader=loader),
        Character(character="O", loader=loader),
        Character(character="S", loader=loader),
    ],
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
    construction_lines=construction_lines,
    dimension_lines=dimension_lines,
)

with open(Path("nixos-logotype-black-dimensioned.svg"), "w") as file:
    file.write(str(my_char_dim.make_dimensioned_svg()))

# close out font because it retains state
loader.font.close()
