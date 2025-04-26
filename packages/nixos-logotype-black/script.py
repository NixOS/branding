from pathlib import Path

from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS
from nixoslogo.logotype import (
    Logotype,
)

my_char = Logotype(
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
)

with open(Path("nixos-logotype-black.svg"), "w") as file:
    file.write(str(my_char.make_svg()))
