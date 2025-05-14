from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS, ClearSpace, LogotypeStyle
from nixoslogo.logotype import Logotype

logotype = Logotype(
    characters="NixOS",
    color="black",
    style=LogotypeStyle.REGULAR,
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
    clear_space=ClearSpace.MINIMAL,
)
logotype.write_svg()
