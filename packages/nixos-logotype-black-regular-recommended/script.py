from nixoslogo.core import DEFAULT_LOGOTYPE_SPACINGS
from nixoslogo.logotype import Logotype

logotype = Logotype(
    spacings=DEFAULT_LOGOTYPE_SPACINGS,
)
logotype.write_svg()
