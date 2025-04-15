from pathlib import Path

from nixoslogo.logotype import (
    DEFAULT_LOGOTYPE_SPACINGS,
    Character,
    Characters,
    FontLoader,
)

loader = FontLoader()

my_char = Characters(
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
