from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS, LogotypeStyle
from nixoslogo.logotype import Logotype

logotype = Logotype(
    style=LogotypeStyle.COLOREDX,
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
)
logotype.write_svg()
