from pathlib import Path

from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS, LogotypeStyle
from nixoslogo.logotype import (
    Logotype,
)

my_char = Logotype(
    style=LogotypeStyle.COLOREDX,
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
)

with open(Path("nixos-logotype-black-modified-x.svg"), "w") as file:
    file.write(str(my_char.make_svg()))
