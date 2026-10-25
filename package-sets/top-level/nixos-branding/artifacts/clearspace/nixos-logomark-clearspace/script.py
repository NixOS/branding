from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logomark import Lambda, Logomark

annotations = Annotations.medium(overrides={"construction_lines": {"stroke": "grey"}})
ilc = LogoClearspace(
    logo=Logomark(),
    logo_name="logomark",
    space_object=Lambda(gap=0),
    annotations=annotations,
)
ilc.write_svg()
