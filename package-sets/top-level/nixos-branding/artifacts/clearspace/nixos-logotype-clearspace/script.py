from nixoslogo.annotations import Annotations
from nixoslogo.artifacts.clearspace import LogoClearspace
from nixoslogo.logotype import Glyph, Logotype

annotations = Annotations.medium()
annotations.construction_lines.stroke = "grey"
space_object = Glyph(character="N")
ilc = LogoClearspace(
    logo=Logotype,
    logo_name="logotype",
    space_object=space_object,
    annotations=annotations,
)
ilc.write_svg()
