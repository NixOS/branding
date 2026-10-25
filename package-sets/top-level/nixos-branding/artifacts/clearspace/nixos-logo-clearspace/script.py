from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logo import NixosLogo
from nixoslogo.logomark import Logomark

annotations = Annotations.large(overrides={"construction_lines": {"stroke": "grey"}})
ilc = LogoClearspace(
    logo=NixosLogo(),
    logo_name="logo",
    space_object=Logomark(),
    annotations=annotations,
)
ilc.write_svg()
