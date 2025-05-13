from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Logomark

annotations = Annotations.large()
annotations.construction_lines.stroke = "grey"
space_object = Logomark()
ilc = LogoClearspace(
    logo=NixosLogo,
    logo_name="logo",
    space_object=space_object,
    annotations=annotations,
)
ilc.write_svg()
