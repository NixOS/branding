from nixoslogo.core import ClearSpace, LogotypeStyle
from nixoslogo.logo import NixosLogo

logo = NixosLogo(
    clear_space=ClearSpace.MINIMAL, logotype_style=LogotypeStyle.LAMBDAPRIME
)
logo.write_svg("nixos-logo-misuse-lambdaprime")
