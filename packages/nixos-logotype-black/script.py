from pathlib import Path

from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS
from nixoslogo.logotype import (
    Character,
    FontLoader,
    Logotype,
)

loader = FontLoader()

my_char = Logotype(
    characters=[
        Character(character="N", loader=loader),
        Character(character="i", loader=loader),
        Character(character="x", loader=loader),
        Character(character="O", loader=loader),
        Character(character="S", loader=loader),
    ],
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
)

with open(Path("nixos-logotype-black.svg"), "w") as file:
    file.write(str(my_char.make_svg()))

# close out font because it retains state
loader.font.close()
