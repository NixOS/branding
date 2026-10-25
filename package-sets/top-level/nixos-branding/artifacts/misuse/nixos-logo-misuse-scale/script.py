from nixoslogo.core import ClearSpace
from nixoslogo.logo import NixosLogo

logo = NixosLogo(clear_space=ClearSpace.MINIMAL, logotype_cap_height=512)
logo.write_svg("nixos-logo-misuse-scale")
