from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logomark import Lambda, Logomark

annotations = Annotations.medium()
annotations.construction_lines.stroke = "grey"
space_object = Lambda(gap=0)
ilc = LogoClearspace(
    logo=Logomark,
    logo_name="logomark",
    space_object=space_object,
    annotations=annotations,
)
ilc.write_svg()
